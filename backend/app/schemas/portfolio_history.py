"""Response shapes for the portfolio history."""

import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.schemas.common import CENTS, round_decimal
from app.services.portfolio_history import HistoryPoint


class PortfolioHistoryPoint(BaseModel):
    """The value of the open positions at the end of one date.

    Decimals are sent as JSON strings to keep precision. Money is rounded to
    cents.
    """

    date: datetime.date
    market_value: Decimal
    cost_basis: Decimal
    unrealised_pnl: Decimal

    @classmethod
    def from_point(cls, point: HistoryPoint) -> "PortfolioHistoryPoint":
        return cls(
            date=point.as_of,
            market_value=round_decimal(point.market_value, CENTS),
            cost_basis=round_decimal(point.cost_basis, CENTS),
            unrealised_pnl=round_decimal(point.unrealised_pnl, CENTS),
        )
