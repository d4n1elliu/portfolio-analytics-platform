"""The rules for one row of a prices CSV. Uses no database."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.models.common import UNIT_PRICE
from app.services.csv_parsing import (
    Row,
    RowError,
    RowErrors,
    parse_date,
    parse_decimal,
    parse_ticker,
    validate_all,
)
from app.services.price_provider import DailyClose

REQUIRED_COLUMNS = ("price_date", "ticker", "close")


@dataclass(frozen=True)
class ValidatedPrice:
    """A row that passed every check, with its values converted from text."""

    price_date: date
    ticker: str
    close: Decimal


def validate_row(
    row: dict[str, str],
    row_number: int,
    known_tickers: set[str],
    today: date,
) -> tuple[ValidatedPrice | None, list[RowError]]:
    """Check one row. Returns the price, or None and every error found."""
    errors = RowErrors(row_number)

    price_date = parse_date(row.get("price_date", ""), "price_date", today, errors)
    ticker = parse_ticker(row.get("ticker", ""), "ticker", known_tickers, errors)
    close = parse_decimal(row.get("close", ""), "close", UNIT_PRICE, errors)

    if errors.errors:
        return None, errors.errors
    return ValidatedPrice(price_date, ticker, close), []


def validate_rows(
    rows: list[Row], known_tickers: set[str], today: date
) -> tuple[list[ValidatedPrice], list[RowError]]:
    """Check every row and return all the valid prices and all the errors.

    A security can have one price per day, so a repeated ticker and date is an error.
    """
    first_rows: dict[tuple[str, date], int] = {}

    def validate(row: dict[str, str], row_number: int):
        price, errors = validate_row(row, row_number, known_tickers, today)
        if price is None:
            return None, errors
        first_row = first_rows.setdefault((price.ticker, price.price_date), row_number)
        if first_row != row_number:
            message = f"{price.ticker} already has a price for {price.price_date} on row {first_row}."
            return None, [RowError(row_number, "price_date", message)]
        return price, []

    return validate_all(rows, validate)


def closes_by_ticker(prices: Iterable[ValidatedPrice]) -> dict[str, list[DailyClose]]:
    closes: dict[str, list[DailyClose]] = {}
    for price in prices:
        closes.setdefault(price.ticker, []).append(DailyClose(price.price_date, price.close))
    return closes
