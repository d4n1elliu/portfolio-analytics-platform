"""Unit tests for the trade row rules.

No database is used. The known tickers and today's date are passed in, so
the results are the same on any machine on any day.
"""

from datetime import date
from decimal import Decimal

import pytest

from app.models import TradeSide
from app.services.trade_csv import REQUIRED_COLUMNS, validate_row, validate_rows

KNOWN_TICKERS = {"BHP", "CBA", "VAS"}
TODAY = date(2026, 6, 30)
ROW_NUMBER = 2


def make_row(**changes: str) -> dict[str, str]:
    """Return a valid row, with any given columns replaced."""
    row = {
        "trade_date": "2026-03-16",
        "ticker": "BHP",
        "side": "BUY",
        "quantity": "100",
        "price": "45.25",
        "fees": "19.95",
    }
    row.update(changes)
    return row


def validate(row: dict[str, str]):
    return validate_row(row, ROW_NUMBER, KNOWN_TICKERS, TODAY)


def assert_valid(row: dict[str, str]):
    trade, errors = validate(row)
    assert errors == []
    assert trade is not None
    return trade


def assert_single_error(row: dict[str, str], column: str, message_part: str) -> None:
    trade, errors = validate(row)
    assert trade is None
    assert len(errors) == 1
    assert errors[0].row == ROW_NUMBER
    assert errors[0].column == column
    assert message_part in errors[0].message


# --- Valid rows ---


def test_valid_row_is_converted_to_typed_values():
    trade = assert_valid(make_row())

    assert trade.trade_date == date(2026, 3, 16)
    assert trade.ticker == "BHP"
    assert trade.side is TradeSide.BUY
    assert trade.quantity == Decimal("100")
    assert trade.price == Decimal("45.25")
    assert trade.fees == Decimal("19.95")


def test_numbers_keep_their_exact_decimal_value():
    trade = assert_valid(make_row(quantity="0.1", price="4.215"))

    # A float would turn 0.1 into 0.1000000000000000055.
    assert str(trade.quantity) == "0.1"
    assert str(trade.price) == "4.215"


def test_trade_dated_today_is_allowed():
    assert_valid(make_row(trade_date=TODAY.isoformat()))


def test_ticker_is_case_insensitive():
    assert assert_valid(make_row(ticker="bhp")).ticker == "BHP"


# --- Side ---


@pytest.mark.parametrize("side", ["buy", "Buy", "sell", "SeLL"])
def test_side_is_case_insensitive(side: str):
    assert assert_valid(make_row(side=side)).side is TradeSide(side.upper())


def test_unknown_side_is_rejected():
    assert_single_error(make_row(side="HOLD"), "side", "BUY or SELL")


# --- Fees (optional) ---


def test_missing_fees_column_defaults_to_zero():
    row = make_row()
    del row["fees"]

    assert assert_valid(row).fees == Decimal("0")


def test_empty_fees_value_defaults_to_zero():
    assert assert_valid(make_row(fees="")).fees == Decimal("0")


def test_zero_fees_are_allowed():
    assert_valid(make_row(fees="0"))


def test_negative_fees_are_rejected():
    assert_single_error(make_row(fees="-1"), "fees", "0 or more")


# --- Date ---


@pytest.mark.parametrize("value", ["16/03/2026", "2026-13-01", "2026-02-30", "yesterday"])
def test_invalid_date_is_rejected(value: str):
    assert_single_error(make_row(trade_date=value), "trade_date", "YYYY-MM-DD")


def test_future_date_is_rejected():
    assert_single_error(make_row(trade_date="2026-07-01"), "trade_date", "future")


# --- Ticker ---


def test_unknown_ticker_is_rejected():
    assert_single_error(make_row(ticker="XYZ"), "ticker", "not a known security")


# --- Quantity and price ---


@pytest.mark.parametrize("value", ["0", "-5"])
def test_quantity_must_be_greater_than_zero(value: str):
    assert_single_error(make_row(quantity=value), "quantity", "greater than 0")


@pytest.mark.parametrize("value", ["0", "-45.25"])
def test_price_must_be_greater_than_zero(value: str):
    assert_single_error(make_row(price=value), "price", "greater than 0")


@pytest.mark.parametrize("value", ["abc", "1,000", "$45.25", "1e3", "NaN", "Infinity"])
def test_text_that_is_not_a_plain_number_is_rejected(value: str):
    assert_single_error(make_row(price=value), "price", "not a number")


def test_more_decimal_places_than_the_column_stores_is_rejected():
    assert_single_error(make_row(price="45.1234567"), "price", "at most 6 decimal places")
    assert_single_error(make_row(fees="9.999"), "fees", "at most 2 decimal places")


def test_number_too_large_for_the_column_is_rejected():
    assert_single_error(make_row(quantity="1000000000000"), "quantity", "too large")


# --- Required values ---


@pytest.mark.parametrize("column", REQUIRED_COLUMNS)
def test_empty_required_value_is_rejected(column: str):
    assert_single_error(make_row(**{column: ""}), column, "is required")


@pytest.mark.parametrize("column", REQUIRED_COLUMNS)
def test_missing_required_value_is_rejected(column: str):
    row = make_row()
    del row[column]

    assert_single_error(row, column, "is required")


def test_every_error_in_a_row_is_reported():
    trade, errors = validate(make_row(ticker="XYZ", side="HOLD", quantity="0"))

    assert trade is None
    assert [error.column for error in errors] == ["ticker", "side", "quantity"]


# --- Whole file ---


def test_validate_rows_collects_trades_and_errors_with_their_row_numbers():
    rows = [
        (2, make_row()),
        (3, make_row(ticker="XYZ")),
        (4, make_row(side="sell", ticker="CBA")),
        (5, make_row(price="0")),
    ]

    trades, errors = validate_rows(rows, KNOWN_TICKERS, TODAY)

    assert [trade.ticker for trade in trades] == ["BHP", "CBA"]
    assert [(error.row, error.column) for error in errors] == [(3, "ticker"), (5, "price")]
