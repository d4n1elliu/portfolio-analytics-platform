"""Response shapes for holdings."""

from decimal import ROUND_HALF_UP, Decimal

from pydantic import BaseModel

from app.services.holdings import Holding

CENTS = Decimal("0.01")
UNIT_COST_PLACES = Decimal("0.000001")


class HoldingRead(BaseModel):
    """The position in one security.

    Decimals are sent as JSON strings to keep precision. Money is rounded to
    cents and average cost to six decimal places.
    """

    ticker: str
    security_name: str
    sector: str
    asset_class: str
    currency: str
    quantity: Decimal
    # None when nothing is held.
    average_cost: Decimal | None
    cost_basis: Decimal
    realised_pnl: Decimal
    # Units sold that were never held. Zero unless the trades are wrong.
    oversold_quantity: Decimal

    @classmethod
    def from_holding(cls, holding: Holding) -> "HoldingRead":
        security, position = holding.security, holding.position
        average_cost = position.average_cost
        return cls(
            ticker=security.ticker,
            security_name=security.name,
            sector=security.sector,
            asset_class=security.asset_class,
            currency=security.currency,
            quantity=position.quantity,
            average_cost=None if average_cost is None else _round(average_cost, UNIT_COST_PLACES),
            cost_basis=_round(position.cost_basis, CENTS),
            realised_pnl=_round(position.realised_pnl, CENTS),
            oversold_quantity=position.oversold_quantity,
        )


def _round(value: Decimal, places: Decimal) -> Decimal:
    return value.quantize(places, rounding=ROUND_HALF_UP)
