"""Response shapes for holdings."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.schemas.common import CENTS, FRACTION_PLACES, round_decimal
from app.services.holdings import Holding
from app.services.valuation import Valuation

UNIT_COST_PLACES = Decimal("0.000001")


class HoldingRead(BaseModel):
    """The position in one security.

    Decimals are sent as JSON strings to keep precision. Money is rounded to
    cents, and average cost, return and weight to six decimal places.
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
    # The fields below are None when the position is closed or has no stored price.
    last_price: Decimal | None
    price_date: date | None
    market_value: Decimal | None
    unrealised_pnl: Decimal | None
    # Fractions, such as 0.0886 for 8.86%.
    unrealised_return: Decimal | None
    weight: Decimal | None

    @classmethod
    def from_holding(cls, holding: Holding) -> "HoldingRead":
        security, position, valuation = holding.security, holding.position, holding.valuation
        average_cost = position.average_cost
        return cls(
            ticker=security.ticker,
            security_name=security.name,
            sector=security.sector,
            asset_class=security.asset_class,
            currency=security.currency,
            quantity=position.quantity,
            average_cost=_round_optional(average_cost, UNIT_COST_PLACES),
            cost_basis=round_decimal(position.cost_basis, CENTS),
            realised_pnl=round_decimal(position.realised_pnl, CENTS),
            oversold_quantity=position.oversold_quantity,
            weight=_round_optional(holding.weight, FRACTION_PLACES),
            **_valuation_fields(valuation),
        )


def _valuation_fields(valuation: Valuation | None) -> dict[str, Decimal | date | None]:
    """The price and valuation fields of the response, rounded."""
    if valuation is None:
        return dict.fromkeys(
            ("last_price", "price_date", "market_value", "unrealised_pnl", "unrealised_return")
        )
    return {
        "last_price": valuation.last_price,
        "price_date": valuation.price_date,
        "market_value": round_decimal(valuation.market_value, CENTS),
        "unrealised_pnl": round_decimal(valuation.unrealised_pnl, CENTS),
        "unrealised_return": _round_optional(valuation.unrealised_return, FRACTION_PLACES),
    }


def _round_optional(value: Decimal | None, places: Decimal) -> Decimal | None:
    return None if value is None else round_decimal(value, places)
