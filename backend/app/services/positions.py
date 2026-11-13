"""Work out the position in one security from its trades. Uses no database.

Uses weighted average cost: a buy changes the average cost per unit, and a
sell removes units at the current average.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal

from app.models import Trade, TradeSide

ZERO = Decimal("0")


@dataclass(frozen=True)
class Position:
    """What the fund holds in one security. Values are not rounded."""

    quantity: Decimal
    # Cost of the units still held, including buy fees.
    cost_basis: Decimal
    realised_pnl: Decimal
    # Units sold that were never held.
    oversold_quantity: Decimal

    @property
    def is_open(self) -> bool:
        return self.quantity > ZERO

    @property
    def average_cost(self) -> Decimal | None:
        """None when nothing is held."""
        return self.cost_basis / self.quantity if self.is_open else None


def calculate_position(trades: Iterable[Trade]) -> Position:
    """Return the position for one security's trades, given oldest first."""
    quantity = ZERO
    cost_basis = ZERO
    realised_pnl = ZERO
    oversold_quantity = ZERO

    for trade in trades:
        if trade.side == TradeSide.BUY:
            cost_basis += trade.quantity * trade.price + trade.fees
            quantity += trade.quantity
            continue

        # A sell can be larger than the position. Only the units held are sold.
        sold = min(trade.quantity, quantity)
        oversold_quantity += trade.quantity - sold
        if sold == ZERO:
            continue

        # Selling everything removes the whole cost, so division leaves no remainder.
        cost_of_sold = cost_basis if sold == quantity else cost_basis / quantity * sold
        # Only the sold share of the fees is counted.
        proceeds = sold * trade.price - trade.fees * sold / trade.quantity

        realised_pnl += proceeds - cost_of_sold
        cost_basis -= cost_of_sold
        quantity -= sold

    return Position(quantity, cost_basis, realised_pnl, oversold_quantity)
