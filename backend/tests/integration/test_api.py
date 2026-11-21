"""The API from sign in to the Dashboard figures, with PostgreSQL behind it."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from app.models import Role
from app.services.price_provider import DailyClose
from app.services.prices import insert_new_closes
from app.services.securities import security_ids_by_ticker
from factories import make_user, sign_in
from scripts.seed import SECURITIES, seed_securities

SAMPLE_DATA = Path(__file__).resolve().parents[2] / "sample_data"
SAMPLE_TRADES = 30
PRICE_DATE = date(2026, 11, 13)


@pytest.fixture
def client(db, save, client_with_session):
    seed_securities(db, SECURITIES)
    save(make_user(Role.OPERATIONS))
    client = client_with_session(db)
    sign_in(client, Role.OPERATIONS)
    return client


def import_file(client, name: str):
    with (SAMPLE_DATA / name).open("rb") as file:
        return client.post("/trades/import", files={"file": (name, file, "text/csv")})


def import_sample_and_price_bhp(client, db) -> None:
    import_file(client, "trades_sample.csv")
    bhp_id = security_ids_by_ticker(db)["BHP"]
    insert_new_closes(db, bhp_id, [DailyClose(PRICE_DATE, Decimal("46"))])


def test_imported_trades_are_listed_newest_first(client):
    response = import_file(client, "trades_sample.csv")
    assert response.status_code == 201
    assert response.json() == {"imported": SAMPLE_TRADES}

    page = client.get("/trades", params={"limit": 10}).json()

    assert page["total"] == SAMPLE_TRADES
    assert len(page["items"]) == 10
    dates = [trade["trade_date"] for trade in page["items"]]
    assert dates == sorted(dates, reverse=True)


def test_the_same_file_cannot_be_imported_twice(client):
    import_file(client, "trades_sample.csv")

    response = import_file(client, "trades_sample.csv")

    assert response.status_code == 409
    assert response.json()["detail"].startswith(
        "This file was already imported as 'trades_sample.csv' on "
    )
    assert response.json()["detail"].endswith("by Test operations. Nothing was saved.")
    assert client.get("/trades").json()["total"] == SAMPLE_TRADES


def test_an_import_is_recorded_with_who_made_it(client):
    import_file(client, "trades_sample.csv")

    imports = client.get("/trades/imports").json()

    assert imports["total"] == 1
    assert imports["items"][0]["file_name"] == "trades_sample.csv"
    assert imports["items"][0]["row_count"] == SAMPLE_TRADES
    assert imports["items"][0]["imported_by"] == "Test operations"


def test_trades_can_be_filtered_sorted_and_exported(client):
    import_file(client, "trades_sample.csv")
    bhp_by_quantity = {"ticker": "bhp", "sort": "quantity", "order": "asc"}

    page = client.get("/trades", params=bhp_by_quantity).json()
    export = client.get("/trades/export", params=bhp_by_quantity)

    assert page["total"] == 3
    assert [trade["quantity"] for trade in page["items"]] == [
        "200.000000",
        "250.000000",
        "400.000000",
    ]
    assert export.text.splitlines() == [
        "trade_date,ticker,side,quantity,price,fees",
        "2026-02-17,BHP,BUY,200.000000,43.100000,19.95",
        "2026-05-05,BHP,SELL,250.000000,45.720000,29.95",
        "2025-11-18,BHP,BUY,400.000000,41.850000,29.95",
    ]


def test_a_rejected_import_saves_nothing(client):
    response = import_file(client, "trades_invalid.csv")

    assert response.status_code == 422
    assert client.get("/trades").json()["total"] == 0
    assert client.get("/trades/imports").json()["total"] == 0


def test_holdings_are_calculated_and_valued_from_the_stored_rows(client, db):
    import_sample_and_price_bhp(client, db)

    holdings = {holding["ticker"]: holding for holding in client.get("/holdings").json()}

    bhp = holdings["BHP"]
    assert bhp["quantity"] == "350.000000"
    assert bhp["cost_basis"] == "14822.44"
    assert bhp["realised_pnl"] == "812.59"
    assert bhp["last_price"] == "46.000000"
    assert bhp["market_value"] == "16100.00"
    assert bhp["weight"] == "1.000000"
    assert holdings["CBA"]["market_value"] is None


def test_history_and_performance_use_the_stored_prices(client, db):
    import_sample_and_price_bhp(client, db)

    history = client.get("/portfolio/history").json()
    performance = client.get("/portfolio/performance").json()

    assert [(point["date"], point["market_value"]) for point in history] == [
        ("2026-11-13", "16100.00")
    ]
    assert performance["as_of"] == "2026-11-13"
    assert len(performance["growth"]) == 1


def test_the_database_health_check_runs_a_query(client):
    assert client.get("/health/db").json() == {"status": "ok", "database": "connected"}
