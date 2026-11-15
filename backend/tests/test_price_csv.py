"""Unit tests for the price row rules. No database or network is used."""

from datetime import date
from decimal import Decimal

from app.services.csv_parsing import decode_csv, read_rows
from app.services.price_csv import (
    REQUIRED_COLUMNS,
    closes_by_ticker,
    validate_row,
    validate_rows,
)
from app.services.price_provider import DailyClose
from jobs.seed_prices import MAX_ROWS, PRICE_HISTORY_FILE
from scripts.seed import SECURITIES

KNOWN_TICKERS = {"BHP", "CBA", "VAS"}
TODAY = date(2026, 11, 13)
ROW_NUMBER = 2


def make_row(**changes: str) -> dict[str, str]:
    """Return a valid row, with any given columns replaced."""
    row = {"price_date": "2026-11-12", "ticker": "BHP", "close": "60.3900"}
    row.update(changes)
    return row


def validate(row: dict[str, str]):
    return validate_row(row, ROW_NUMBER, KNOWN_TICKERS, TODAY)


def assert_single_error(row: dict[str, str], column: str, message_part: str) -> None:
    price, errors = validate(row)
    assert price is None
    assert len(errors) == 1
    assert errors[0].row == ROW_NUMBER
    assert errors[0].column == column
    assert message_part in errors[0].message


def numbered(*rows: dict[str, str]) -> list[tuple[int, dict[str, str]]]:
    """Number the rows the way a CSV file does: the header is row 1."""
    return list(enumerate(rows, start=2))


# --- Valid rows ---


def test_valid_row_is_converted_to_typed_values():
    price, errors = validate(make_row())

    assert errors == []
    assert price.price_date == date(2026, 11, 12)
    assert price.ticker == "BHP"
    assert price.close == Decimal("60.39")


def test_ticker_is_matched_ignoring_case():
    price, _ = validate(make_row(ticker="bhp"))

    assert price.ticker == "BHP"


def test_a_price_dated_today_is_allowed():
    price, errors = validate(make_row(price_date="2026-11-13"))

    assert errors == []
    assert price.price_date == TODAY


# --- Invalid rows ---


def test_each_column_is_required():
    for column in REQUIRED_COLUMNS:
        assert_single_error(make_row(**{column: ""}), column, "is required")


def test_date_must_be_a_real_date():
    assert_single_error(make_row(price_date="13/11/2026"), "price_date", "not a valid date")


def test_date_cannot_be_in_the_future():
    assert_single_error(make_row(price_date="2026-11-14"), "price_date", "in the future")


def test_ticker_must_be_a_known_security():
    assert_single_error(make_row(ticker="XYZ"), "ticker", "not a known security")


def test_close_must_be_a_number():
    assert_single_error(make_row(close="sixty"), "close", "not a number")


def test_close_must_be_greater_than_zero():
    assert_single_error(make_row(close="0"), "close", "greater than 0")
    assert_single_error(make_row(close="-5"), "close", "greater than 0")


def test_close_cannot_have_more_than_six_decimal_places():
    price, errors = validate(make_row(close="60.1234567"))

    assert price is None
    assert errors[0].column == "close"


def test_every_error_in_a_row_is_reported():
    price, errors = validate(make_row(price_date="nope", ticker="XYZ", close="-1"))

    assert price is None
    assert [error.column for error in errors] == ["price_date", "ticker", "close"]


# --- Checking a whole file ---


def test_all_valid_rows_are_returned():
    rows = numbered(make_row(), make_row(ticker="CBA", close="166.94"))

    prices, errors = validate_rows(rows, KNOWN_TICKERS, TODAY)

    assert errors == []
    assert [price.ticker for price in prices] == ["BHP", "CBA"]


def test_a_repeated_ticker_and_date_is_an_error_naming_the_first_row():
    rows = numbered(make_row(), make_row(ticker="CBA"), make_row(close="61"))

    prices, errors = validate_rows(rows, KNOWN_TICKERS, TODAY)

    assert [price.ticker for price in prices] == ["BHP", "CBA"]
    assert len(errors) == 1
    assert errors[0].row == 4
    assert errors[0].column == "price_date"
    assert "row 2" in errors[0].message


def test_the_same_ticker_on_different_dates_is_fine():
    rows = numbered(make_row(), make_row(price_date="2026-11-13"))

    _, errors = validate_rows(rows, KNOWN_TICKERS, TODAY)

    assert errors == []


def test_valid_and_invalid_rows_are_both_reported():
    rows = numbered(make_row(), make_row(ticker="XYZ"))

    prices, errors = validate_rows(rows, KNOWN_TICKERS, TODAY)

    assert len(prices) == 1
    assert errors[0].row == 3


# --- Grouping by ticker ---


def test_prices_are_grouped_into_the_closes_of_each_ticker():
    rows = numbered(
        make_row(),
        make_row(ticker="CBA", close="166.94"),
        make_row(price_date="2026-11-13", close="58.86"),
    )
    prices, _ = validate_rows(rows, KNOWN_TICKERS, TODAY)

    assert closes_by_ticker(prices) == {
        "BHP": [
            DailyClose(date(2026, 11, 12), Decimal("60.39")),
            DailyClose(date(2026, 11, 13), Decimal("58.86")),
        ],
        "CBA": [DailyClose(date(2026, 11, 12), Decimal("166.94"))],
    }


# --- The committed price history ---


def test_committed_price_history_is_valid_and_covers_every_security():
    tickers = {security["ticker"] for security in SECURITIES}
    rows = read_rows(decode_csv(PRICE_HISTORY_FILE.read_bytes()), REQUIRED_COLUMNS, MAX_ROWS)

    # date.max, so the file stays valid whenever the tests are run.
    prices, errors = validate_rows(rows, tickers, date.max)

    assert errors == []
    closes = closes_by_ticker(prices)
    assert set(closes) == tickers
    # About a year of trading days for every security.
    assert all(len(ticker_closes) >= 240 for ticker_closes in closes.values())
