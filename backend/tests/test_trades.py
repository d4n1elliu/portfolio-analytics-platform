"""The trades endpoints and the CSV export. No database is used."""

from datetime import date
from decimal import Decimal

import pytest

from app.services.trade_export import trades_to_csv
from factories import buy, make_security, sell

HEADER = "trade_date,ticker,side,quantity,price,fees"


def test_an_export_has_one_row_per_trade_in_the_order_given():
    bhp = make_security("BHP")
    trades = [
        sell(bhp, "250", "45.72", fees="29.95", on=date(2026, 5, 5)),
        buy(bhp, "0.5", "41.85", on=date(2025, 11, 18)),
    ]

    assert trades_to_csv(trades).splitlines() == [
        HEADER,
        "2026-05-05,BHP,SELL,250,45.72,29.95",
        "2025-11-18,BHP,BUY,0.5,41.85,0",
    ]


def test_an_export_of_no_trades_is_just_the_header():
    assert trades_to_csv([]) == HEADER + "\n"


def test_the_export_is_downloaded_as_a_csv_file(client_with_data):
    trade = buy(make_security("BHP"), "10", "40")
    trade.fees = Decimal("1.50")

    response = client_with_data([trade]).get("/trades/export")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert response.headers["content-disposition"] == 'attachment; filename="trades.csv"'
    assert response.text.splitlines()[1].endswith(",BHP,BUY,10,40,1.50")


@pytest.mark.parametrize(
    "params",
    [
        {"sort": "security_name"},
        {"order": "up"},
        {"side": "HOLD"},
        {"date_from": "yesterday"},
        {"date_from": "2026-11-13", "date_to": "2026-11-12"},
    ],
    ids=["unknown column", "unknown order", "unknown side", "not a date", "dates the wrong way"],
)
@pytest.mark.parametrize("path", ["/trades", "/trades/export"])
def test_a_filter_or_order_that_makes_no_sense_is_refused(client_with_data, path, params):
    assert client_with_data([]).get(path, params=params).status_code == 422


def test_a_start_date_equal_to_the_end_date_is_accepted(client_with_data):
    same_day = {"date_from": "2026-11-13", "date_to": "2026-11-13"}

    assert client_with_data([]).get("/trades", params=same_day).status_code == 200
