"""Unit tests for the price provider helpers. No network is used."""

from datetime import date
from decimal import Decimal

from app.services.price_provider import (
    DailyClose,
    PriceProvider,
    closes_from_rows,
    to_provider_symbol,
)

DAY_1 = date(2026, 11, 11)
DAY_2 = date(2026, 11, 12)
DAY_3 = date(2026, 11, 13)


def closes(*values: float | None) -> list[Decimal]:
    rows = zip((DAY_1, DAY_2, DAY_3), values, strict=False)
    return [daily_close.close for daily_close in closes_from_rows(rows)]


# --- Provider symbols ---


def test_asx_ticker_gets_the_ax_suffix():
    assert to_provider_symbol("BHP") == "BHP.AX"


def test_symbol_is_upper_case_with_no_spaces():
    assert to_provider_symbol(" bhp ") == "BHP.AX"


# --- Converting rows to closes ---


def test_float_noise_is_rounded_away():
    # Real values returned by Yahoo.
    assert closes(60.389999, 166.940002, 113.449997) == [
        Decimal("60.39"),
        Decimal("166.94"),
        Decimal("113.45"),
    ]


def test_closes_are_decimals_with_four_places():
    close = closes(60.389999)[0]

    assert isinstance(close, Decimal)
    assert str(close) == "60.3900"


def test_a_price_with_many_decimals_is_rounded_half_up():
    assert closes(4.12345, 4.12344) == [Decimal("4.1235"), Decimal("4.1234")]


def test_rows_with_no_price_are_skipped():
    assert closes(None, float("nan"), 41.85) == [Decimal("41.85")]


def test_infinite_prices_are_skipped():
    assert closes(float("inf"), 41.85) == [Decimal("41.85")]


def test_zero_and_negative_prices_are_skipped():
    assert closes(0.0, -5.0, 41.85) == [Decimal("41.85")]


def test_a_price_that_rounds_to_zero_is_skipped():
    assert closes(0.00001) == []


def test_closes_come_back_oldest_first():
    rows = [(DAY_3, 43.0), (DAY_1, 41.0), (DAY_2, 42.0)]

    assert closes_from_rows(rows) == [
        DailyClose(DAY_1, Decimal("41")),
        DailyClose(DAY_2, Decimal("42")),
        DailyClose(DAY_3, Decimal("43")),
    ]


def test_no_rows_gives_no_closes():
    assert closes_from_rows([]) == []


# --- The provider interface ---


class FakeProvider:
    """A provider that returns the closes it was given."""

    def __init__(self, closes: list[DailyClose]):
        self.closes = closes

    def fetch_closes(self, ticker: str, start: date, end: date) -> list[DailyClose]:
        return [close for close in self.closes if start <= close.price_date <= end]


def test_a_fake_provider_counts_as_a_price_provider():
    provider = FakeProvider([DailyClose(DAY_1, Decimal("41")), DailyClose(DAY_3, Decimal("43"))])

    assert isinstance(provider, PriceProvider)
    assert provider.fetch_closes("BHP", DAY_1, DAY_2) == [DailyClose(DAY_1, Decimal("41"))]


def test_an_object_without_fetch_closes_is_not_a_price_provider():
    assert not isinstance(object(), PriceProvider)
