"""The endpoints behind the page for one security, with PostgreSQL behind them."""

from datetime import date

import pytest

from app.models import Role
from factories import buy, closes, make_security, make_user, sell, sign_in

MONDAY = date(2026, 11, 9)
TUESDAY = date(2026, 11, 10)


@pytest.fixture
def client(db, save, client_with_session):
    """A signed-in client. BHP is held and priced, CBA was sold, and CSL was never traded."""
    bhp, cba, _ = save(make_security("BHP"), make_security("CBA"), make_security("CSL"))
    save(buy(bhp, "100", "40", on=MONDAY), buy(cba, "10", "150", on=MONDAY))
    save(sell(cba, "10", "160", on=TUESDAY))
    # Saved newest first, to show the order comes from the query.
    save(*closes(bhp, {TUESDAY: "42", MONDAY: "41"}))
    save(make_user(Role.ANALYST))
    client = client_with_session(db)
    sign_in(client, Role.ANALYST)
    return client


def test_the_position_in_one_security_is_valued_with_its_weight(client):
    holding = client.get("/holdings/bhp").json()

    assert holding["ticker"] == "BHP"
    assert holding["security_name"] == "BHP Limited"
    assert holding["quantity"] == "100.000000"
    assert holding["market_value"] == "4200.00"
    assert holding["weight"] == "1.000000"


def test_a_closed_position_keeps_its_realised_profit(client):
    holding = client.get("/holdings/CBA").json()

    assert holding["quantity"] == "0.000000"
    assert holding["realised_pnl"] == "100.00"
    assert holding["market_value"] is None


def test_a_security_that_was_never_traded_has_a_position_of_zero(client):
    holding = client.get("/holdings/CSL").json()

    assert holding["ticker"] == "CSL"
    assert holding["quantity"] == "0"
    assert holding["cost_basis"] == "0.00"
    assert holding["average_cost"] is None


def test_the_prices_of_one_security_are_listed_oldest_first(client):
    assert client.get("/securities/bhp/prices").json() == [
        {"date": "2026-11-09", "close": "41.000000"},
        {"date": "2026-11-10", "close": "42.000000"},
    ]
    assert client.get("/securities/CSL/prices").json() == []


@pytest.mark.parametrize("path", ["/holdings/XYZ", "/securities/XYZ/prices"])
def test_an_unknown_ticker_is_not_found(client, path):
    response = client.get(path)

    assert response.status_code == 404
    assert response.json() == {"detail": "No security has the ticker 'XYZ'."}
