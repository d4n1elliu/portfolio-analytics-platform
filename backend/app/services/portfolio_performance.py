"""How well the portfolio has done, as a time-weighted return.

A time-weighted return measures the investments, not the timing of money
going in and out: each day's gain is taken on the value held at the start of
that day, and the days are multiplied together.
"""

import calendar
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.services.portfolio_history import HistoryPoint, list_portfolio_history
from app.services.positions import ZERO

ONE = Decimal("1")

# Months to look back for each period. Year to date and since inception are
# worked out separately.
MONTHS_BACK = {"1m": 1, "3m": 3, "1y": 12}
YEAR_TO_DATE = "ytd"
SINCE_INCEPTION = "inception"
PERIODS = ("1m", "3m", YEAR_TO_DATE, "1y", SINCE_INCEPTION)


@dataclass(frozen=True)
class GrowthPoint:
    """What 1 invested at the start is worth at the end of one date. Not rounded."""

    as_of: date
    growth: Decimal


@dataclass(frozen=True)
class PeriodReturn:
    period: str
    # A fraction, such as 0.0886 for 8.86%. None when the history does not
    # reach back to the start of the period.
    portfolio_return: Decimal | None
    # The date the return is measured from. None when there is no return.
    start: date | None


@dataclass(frozen=True)
class Performance:
    # The latest priced date, or None when there is no history.
    as_of: date | None
    periods: list[PeriodReturn]
    growth: list[GrowthPoint]


def list_performance(db: Session) -> Performance:
    return build_performance(list_portfolio_history(db))


def build_performance(points: Sequence[HistoryPoint]) -> Performance:
    """Work out the return over each period. Uses no database."""
    growth = build_growth(points)
    if not growth:
        return Performance(None, [PeriodReturn(period, None, None) for period in PERIODS], [])

    as_of = growth[-1].as_of
    periods = [
        PeriodReturn(period, *return_since(growth, period_start(period, as_of)))
        for period in PERIODS
    ]
    return Performance(as_of, periods, growth)


def build_growth(points: Sequence[HistoryPoint]) -> list[GrowthPoint]:
    """Multiply the daily returns together, oldest first."""
    growth = []
    factor = ONE
    previous_value = ZERO
    for point in points:
        factor *= ONE + daily_return(previous_value, point)
        growth.append(GrowthPoint(point.as_of, factor))
        previous_value = point.market_value
    return growth


def daily_return(previous_value: Decimal, point: HistoryPoint) -> Decimal:
    """Return the gain on one date as a fraction, leaving out cash put in or taken out."""
    if previous_value > ZERO:
        return (point.market_value - point.net_flow) / previous_value - ONE
    # Nothing was held at the start of the date, so the gain is measured on
    # the cash put in that day.
    if point.net_flow > ZERO:
        return point.market_value / point.net_flow - ONE
    return ZERO


def period_start(period: str, as_of: date) -> date | None:
    """Return the date a period is measured from, or None for since inception."""
    if period == SINCE_INCEPTION:
        return None
    if period == YEAR_TO_DATE:
        return date(as_of.year - 1, 12, 31)
    return months_before(as_of, MONTHS_BACK[period])


def months_before(day: date, months: int) -> date:
    """Step back whole months, keeping the day where the month has it: 31 Mar gives 28 Feb."""
    month_index = day.year * 12 + day.month - 1 - months
    year, month = divmod(month_index, 12)
    last_day = calendar.monthrange(year, month + 1)[1]
    return date(year, month + 1, min(day.day, last_day))


def return_since(
    growth: Sequence[GrowthPoint], start: date | None
) -> tuple[Decimal | None, date | None]:
    """Return the gain to the latest date as a fraction, and the date it is measured from.

    Measured from the last point on or before the start date, or from the
    first point when start is None. Both are None when the history begins
    after the start date, or when everything had been lost by then.
    """
    latest = growth[-1].growth
    if start is None:
        return latest - ONE, growth[0].as_of
    base = next((point for point in reversed(growth) if point.as_of <= start), None)
    if base is None or base.growth == ZERO:
        return None, None
    return latest / base.growth - ONE, base.as_of
