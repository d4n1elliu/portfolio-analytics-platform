"""Response shapes for the portfolio performance."""

import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.schemas.common import FRACTION_PLACES, round_decimal
from app.services.portfolio_performance import Performance


class PeriodReturnRead(BaseModel):
    # One of 1m, 3m, ytd, 1y and inception.
    period: str
    # A fraction, such as 0.0886 for 8.86%. None when the history does not
    # reach back to the start of the period.
    portfolio_return: Decimal | None


class GrowthPointRead(BaseModel):
    date: datetime.date
    # What 1 invested at the start is worth at the end of this date.
    portfolio: Decimal


class PerformanceRead(BaseModel):
    """The time-weighted return of the portfolio.

    Decimals are sent as JSON strings to keep precision, rounded to six
    decimal places.
    """

    # The latest priced date, or None when there is no history.
    as_of: datetime.date | None
    periods: list[PeriodReturnRead]
    growth: list[GrowthPointRead]

    @classmethod
    def from_performance(cls, performance: Performance) -> "PerformanceRead":
        return cls(
            as_of=performance.as_of,
            periods=[
                PeriodReturnRead(
                    period=period.period,
                    portfolio_return=_round_optional(period.portfolio_return),
                )
                for period in performance.periods
            ],
            growth=[
                GrowthPointRead(date=point.as_of, portfolio=_round_optional(point.growth))
                for point in performance.growth
            ],
        )


def _round_optional(value: Decimal | None) -> Decimal | None:
    return None if value is None else round_decimal(value, FRACTION_PLACES)
