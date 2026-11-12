"""The rules for one row of a trades CSV. Uses no database."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.models.common import CASH_AMOUNT, QUANTITY, UNIT_PRICE
from app.models.trade import TradeSide
from app.services.csv_parsing import (
    Row,
    RowError,
    RowErrors,
    parse_date,
    parse_decimal,
    parse_ticker,
    validate_all,
)

REQUIRED_COLUMNS = ("trade_date", "ticker", "side", "quantity", "price")
SIDE_CHOICES = " or ".join(side.value for side in TradeSide)


@dataclass(frozen=True)
class ValidatedTrade:
    """A row that passed every check, with its values converted from text."""

    trade_date: date
    ticker: str
    side: TradeSide
    quantity: Decimal
    price: Decimal
    fees: Decimal


def validate_row(
    row: dict[str, str],
    row_number: int,
    known_tickers: set[str],
    today: date,
) -> tuple[ValidatedTrade | None, list[RowError]]:
    """Check one row. Returns the trade, or None and every error found."""
    errors = RowErrors(row_number)

    trade_date = parse_date(row.get("trade_date", ""), "trade_date", today, errors)
    ticker = parse_ticker(row.get("ticker", ""), "ticker", known_tickers, errors)
    side = _parse_side(row.get("side", ""), errors)
    quantity = parse_decimal(row.get("quantity", ""), "quantity", QUANTITY, errors)
    price = parse_decimal(row.get("price", ""), "price", UNIT_PRICE, errors)
    # fees is optional: a missing column or an empty value means zero.
    fees = parse_decimal(row.get("fees", "") or "0", "fees", CASH_AMOUNT, errors, allow_zero=True)

    if errors.errors:
        return None, errors.errors
    return ValidatedTrade(trade_date, ticker, side, quantity, price, fees), []


def validate_rows(
    rows: list[Row], known_tickers: set[str], today: date
) -> tuple[list[ValidatedTrade], list[RowError]]:
    """Check every row and return all the valid trades and all the errors."""
    return validate_all(
        rows, lambda row, row_number: validate_row(row, row_number, known_tickers, today)
    )


def _parse_side(value: str, errors: RowErrors) -> TradeSide | None:
    if not value:
        errors.add("side", "side is required.")
        return None
    try:
        return TradeSide(value.upper())
    except ValueError:
        errors.add("side", f"'{value}' is not a valid side. Use {SIDE_CHOICES}.")
        return None
