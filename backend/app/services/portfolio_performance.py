"""How well the portfolio has done, as a time-weighted return.

A time-weighted return measures the investments, not the timing of money
going in and out: each day's gain is taken on the value held at the start of
that day, and the days are multiplied together.
"""

import calendar
from bisect import bisect_right
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.config import BENCHMARK_TICKER
from app.services.portfolio_history import HistoryPoint, list_portfolio_history
from app.services.positions import ZERO
from app.services.prices import list_prices_of_security
from app.services.securities import find_by_ticker

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
    benchmark: Decimal | None = None


@dataclass(frozen=True)
class Benchmark:
    ticker: str
    closes: Mapping[date, Decimal]


@dataclass(frozen=True)
class PeriodReturn:
    period: str
    # A fraction, such as 0.0886 for 8.86%. None when the history does not
    # reach back to the start of the period.
    portfolio_return: Decimal | None
    # The date the return is measured from. None when there is no return.
    start: date | None
    benchmark_return: Decimal | None = None


@dataclass(frozen=True)
class Performance:
    # The latest priced date, or None when there is no history.
    as_of: date | None
    periods: list[PeriodReturn]
    growth: list[GrowthPoint]
    benchmark: str | None = None


def list_performance(db: Session) -> Performance:
    return build_performance(list_portfolio_history(db), find_benchmark(db))


def find_benchmark(db: Session) -> Benchmark | None:
    security = find_by_ticker(db, BENCHMARK_TICKER)
    if security is None:
        return None
    prices = list_prices_of_security(db, security.id)
    return Benchmark(security.ticker, {price.price_date: price.close for price in prices})


def build_performance(
    points: Sequence[HistoryPoint], benchmark: Benchmark | None = None
) -> Performance:
    """Work out the return over each period. Uses no database."""
    growth = build_growth(points, benchmark.closes if benchmark else {})
    if not growth:
        return Performance(None, [PeriodReturn(period, None, None) for period in PERIODS], [])

    as_of = growth[-1].as_of
    periods = [
        PeriodReturn(period, *return_since(growth, period_start(period, as_of)))
        for period in PERIODS
    ]
    compared = benchmark is not None and growth[-1].benchmark is not None
    return Performance(as_of, periods, growth, benchmark.ticker if compared else None)


def build_growth(
    points: Sequence[HistoryPoint], benchmark_closes: Mapping[date, Decimal] | None = None
) -> list[GrowthPoint]:
    """Multiply the daily returns together, oldest first."""
    benchmark = benchmark_growth([point.as_of for point in points], benchmark_closes or {})
    growth = []
    factor = ONE
    previous_value = ZERO
    for point, benchmark_factor in zip(points, benchmark):
        factor *= ONE + daily_return(previous_value, point)
        growth.append(GrowthPoint(point.as_of, factor, benchmark_factor))
        previous_value = point.market_value
    return growth


def benchmark_growth(days: Sequence[date], closes: Mapping[date, Decimal]) -> list[Decimal | None]:
    priced_days = sorted(closes)
    growth: list[Decimal | None] = []
    first_close = None
    for day in days:
        close = _latest_close_on_or_before(day, priced_days, closes)
        if close is None:
            growth.append(None)
            continue
        first_close = first_close or close
        growth.append(close / first_close)
    return growth


def _latest_close_on_or_before(
    day: date, priced_days: Sequence[date], closes: Mapping[date, Decimal]
) -> Decimal | None:
    priced_so_far = bisect_right(priced_days, day)
    return closes[priced_days[priced_so_far - 1]] if priced_so_far else None


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
) -> tuple[Decimal | None, date | None, Decimal | None]:
    """Return the gain to the latest date, the date it is measured from, and the benchmark's gain.

    Measured from the last point on or before the start date, or from the
    first point when start is None. All are None when the history begins
    after the start date, or when everything had been lost by then.
    """
    latest = growth[-1]
    if start is None:
        first = growth[0]
        return latest.growth - ONE, first.as_of, _gain(first.benchmark, latest.benchmark)
    base = next((point for point in reversed(growth) if point.as_of <= start), None)
    if base is None or base.growth == ZERO:
        return None, None, None
    return (
        latest.growth / base.growth - ONE,
        base.as_of,
        _gain(base.benchmark, latest.benchmark),
    )


def _gain(start: Decimal | None, end: Decimal | None) -> Decimal | None:
    return None if start is None or end is None else end / start - ONE
