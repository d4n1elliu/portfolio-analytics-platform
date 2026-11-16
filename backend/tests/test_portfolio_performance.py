"""Unit tests for portfolio performance. No database is used."""

from datetime import date
from decimal import Decimal

import pytest

from app.models import Price, Security
from app.services.portfolio_history import build_portfolio_history
from app.services.portfolio_performance import (
    PERIODS,
    build_growth,
    build_performance,
    months_before,
    period_start,
)
from factories import buy, make_security, sell

DAY_1 = date(2026, 11, 9)
DAY_2 = date(2026, 11, 10)
DAY_3 = date(2026, 11, 11)
DAY_4 = date(2026, 11, 12)
DAY_5 = date(2026, 11, 13)
DAY_6 = date(2026, 11, 16)


def closes(security: Security, by_date: dict[date, str]) -> list[Price]:
    return [
        Price(security=security, price_date=day, close=Decimal(close))
        for day, close in by_date.items()
    ]


def growth_of(trades, prices) -> list[Decimal]:
    return [point.growth for point in build_growth(build_portfolio_history(trades, prices))]


def returns_of(trades, prices) -> dict[str, Decimal | None]:
    performance = build_performance(build_portfolio_history(trades, prices))
    return {period.period: period.portfolio_return for period in performance.periods}


# --- Growth: the daily returns multiplied together ---


def test_no_history_gives_no_growth():
    assert build_growth([]) == []


def test_price_rise_with_no_trades_is_the_whole_return():
    bhp = make_security("BHP")
    trades = [buy(bhp, "100", "10", on=DAY_1)]

    # 1,000 put in, worth 1,000 then 1,100: up 10%.
    assert growth_of(trades, closes(bhp, {DAY_1: "10", DAY_2: "11"})) == [
        Decimal("1"),
        Decimal("1.1"),
    ]


def test_buying_more_does_not_count_as_a_gain():
    bhp = make_security("BHP")
    trades = [buy(bhp, "100", "10", on=DAY_1), buy(bhp, "100", "11", on=DAY_3)]
    prices = closes(bhp, {DAY_1: "10", DAY_2: "11", DAY_3: "11", DAY_4: "12.1"})

    # The value doubles on day 3, but only because 1,100 was put in.
    # 10%, then nothing, then 10%: 1.1 x 1.1 = 1.21.
    assert growth_of(trades, prices) == [
        Decimal("1"),
        Decimal("1.1"),
        Decimal("1.1"),
        Decimal("1.21"),
    ]


def test_selling_some_does_not_count_as_a_loss():
    bhp = make_security("BHP")
    trades = [buy(bhp, "100", "10", on=DAY_1), sell(bhp, "50", "11", on=DAY_3)]
    prices = closes(bhp, {DAY_1: "10", DAY_2: "11", DAY_3: "11", DAY_4: "12.1"})

    assert growth_of(trades, prices) == [
        Decimal("1"),
        Decimal("1.1"),
        Decimal("1.1"),
        Decimal("1.21"),
    ]


def test_buying_below_the_close_is_a_gain_on_that_day():
    bhp = make_security("BHP")
    trades = [buy(bhp, "100", "10", on=DAY_1)]

    # 1,000 put in, worth 1,050 at the close.
    assert growth_of(trades, closes(bhp, {DAY_1: "10.5"})) == [Decimal("1.05")]


def test_fees_reduce_the_return():
    bhp = make_security("BHP")
    trades = [buy(bhp, "100", "10", fees="25", on=DAY_1)]

    # 1,025 put in, worth 1,000 at the close.
    assert growth_of(trades, closes(bhp, {DAY_1: "10"})) == [Decimal("1000") / Decimal("1025")]


def test_return_carries_through_selling_everything_and_buying_back():
    bhp = make_security("BHP")
    trades = [
        buy(bhp, "100", "10", on=DAY_1),
        sell(bhp, "100", "11", on=DAY_3),
        buy(bhp, "100", "12", on=DAY_5),
    ]
    prices = closes(
        bhp, {DAY_1: "10", DAY_2: "11", DAY_3: "11", DAY_4: "11.5", DAY_5: "12", DAY_6: "13.2"}
    )

    # Up 10%, sold, out of the market for a day, bought back, up 10% again.
    assert growth_of(trades, prices) == [
        Decimal("1"),
        Decimal("1.1"),
        Decimal("1.1"),
        Decimal("1.1"),
        Decimal("1.1"),
        Decimal("1.21"),
    ]


def test_two_securities_are_weighted_by_their_value():
    bhp, cba = make_security("BHP"), make_security("CBA")
    trades = [buy(bhp, "100", "10", on=DAY_1), buy(cba, "10", "300", on=DAY_1)]
    prices = closes(bhp, {DAY_1: "10", DAY_2: "12"}) + closes(cba, {DAY_1: "300", DAY_2: "300"})

    # 4,000 becomes 4,200: up 5%.
    assert growth_of(trades, prices)[-1] == Decimal("1.05")


# --- Periods ---


def test_every_period_is_returned_in_order():
    performance = build_performance([])

    assert [period.period for period in performance.periods] == list(PERIODS)
    assert performance.as_of is None
    assert {period.portfolio_return for period in performance.periods} == {None}


def test_since_inception_covers_the_whole_history():
    bhp = make_security("BHP")
    trades = [buy(bhp, "100", "10", on=DAY_1)]

    returns = returns_of(trades, closes(bhp, {DAY_1: "10", DAY_2: "11", DAY_3: "12.1"}))

    assert returns["inception"] == Decimal("0.21")


def test_period_longer_than_the_history_has_no_return():
    bhp = make_security("BHP")
    trades = [buy(bhp, "100", "10", on=DAY_1)]

    returns = returns_of(trades, closes(bhp, {DAY_1: "10", DAY_2: "11"}))

    assert returns["1m"] is None
    assert returns["1y"] is None


def test_period_is_measured_from_the_last_point_on_or_before_its_start():
    bhp = make_security("BHP")
    start = date(2026, 10, 9)
    trades = [buy(bhp, "100", "10", on=start)]
    prices = closes(
        bhp, {start: "10", date(2026, 10, 12): "12", date(2026, 10, 16): "15", DAY_3: "18"}
    )

    # One month before 11 Nov is 11 Oct, a Sunday, so the base is 9 Oct.
    assert returns_of(trades, prices)["1m"] == Decimal("0.8")


def test_year_to_date_is_measured_from_the_last_day_of_last_year():
    bhp = make_security("BHP")
    trades = [buy(bhp, "100", "10", on=date(2025, 12, 30))]
    prices = closes(
        bhp, {date(2025, 12, 30): "10", date(2025, 12, 31): "20", date(2026, 1, 2): "25"}
    )

    assert returns_of(trades, prices)["ytd"] == Decimal("0.25")


@pytest.mark.parametrize(
    ("period", "start"),
    [
        ("1m", date(2026, 10, 13)),
        ("3m", date(2026, 8, 13)),
        ("ytd", date(2025, 12, 31)),
        ("1y", date(2025, 11, 13)),
        ("inception", None),
    ],
)
def test_period_start_dates(period, start):
    assert period_start(period, DAY_5) == start


@pytest.mark.parametrize(
    ("day", "months", "expected"),
    [
        (date(2026, 3, 31), 1, date(2026, 2, 28)),
        (date(2024, 3, 31), 1, date(2024, 2, 29)),
        (date(2026, 1, 15), 1, date(2025, 12, 15)),
        (date(2026, 2, 28), 12, date(2025, 2, 28)),
    ],
)
def test_months_before_keeps_the_day_where_the_month_has_it(day, months, expected):
    assert months_before(day, months) == expected
