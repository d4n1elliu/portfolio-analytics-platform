"""Work out what a position is worth at a given price. Uses no database."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.services.positions import ZERO, Position


@dataclass(frozen=True)
class Valuation:
    """A position valued at one closing price. Values are not rounded."""

    last_price: Decimal
    price_date: date
    market_value: Decimal
    unrealised_pnl: Decimal
    # A fraction, such as 0.0886 for 8.86%. None when the position cost nothing.
    unrealised_return: Decimal | None


def value_position(position: Position, close: Decimal, price_date: date) -> Valuation:
    """Value a position at a closing price."""
    market_value = position.quantity * close
    unrealised_pnl = market_value - position.cost_basis
    unrealised_return = (
        unrealised_pnl / position.cost_basis if position.cost_basis != ZERO else None
    )
    return Valuation(close, price_date, market_value, unrealised_pnl, unrealised_return)


def portfolio_weights(market_values: Mapping[str, Decimal]) -> dict[str, Decimal]:
    """Return each holding's share of the total market value, as a fraction."""
    total = sum(market_values.values(), ZERO)
    if total == ZERO:
        return {}
    return {ticker: value / total for ticker, value in market_values.items()}
