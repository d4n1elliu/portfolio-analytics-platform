"""The shape of a price provider, and how its prices become Decimals.

Uses no database and no network.
"""

import math
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Protocol, runtime_checkable

ASX_SUFFIX = ".AX"
CLOSE_PLACES = Decimal("0.0001")


@dataclass(frozen=True)
class DailyClose:
    price_date: date
    close: Decimal


class ProviderError(Exception):
    """Raised when a provider cannot return prices."""


@runtime_checkable
class PriceProvider(Protocol):
    def fetch_closes(self, ticker: str, start: date, end: date) -> list[DailyClose]:
        """Return the closes from start to end, both dates included.

        An empty list means no trading days. Raises ProviderError on failure.
        """
        ...


def to_provider_symbol(ticker: str) -> str:
    """Turn an ASX ticker into the provider's symbol: BHP becomes BHP.AX."""
    return f"{ticker.strip().upper()}{ASX_SUFFIX}"


def closes_from_rows(rows: Iterable[tuple[date, float | None]]) -> list[DailyClose]:
    """Turn a provider's rows into closes, oldest first.

    Rows without a usable price are skipped. Floats stop here: everything
    returned is a Decimal.
    """
    closes = []
    for price_date, value in rows:
        close = _to_decimal(value)
        if close is not None:
            closes.append(DailyClose(price_date, close))
    return sorted(closes, key=lambda daily_close: daily_close.price_date)


def _to_decimal(value: float | None) -> Decimal | None:
    """Round a price to four places. Returns None if it is missing or not above zero."""
    if value is None or not math.isfinite(value):
        return None
    # str() first, so float noise such as 60.389999 rounds to 60.39.
    close = Decimal(str(value)).quantize(CLOSE_PLACES, rounding=ROUND_HALF_UP)
    return close if close > 0 else None
