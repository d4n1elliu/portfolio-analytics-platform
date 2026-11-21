"""Unit tests for the price refresh. No database or network is used."""

from datetime import date
from decimal import Decimal

from app.models import Security
from app.services.price_provider import DailyClose, ProviderError
from app.services.price_refresh import RefreshResult, refresh_securities, refresh_window

TODAY = date(2026, 11, 13)


def make_security(security_id: int, ticker: str) -> Security:
    return Security(
        id=security_id, ticker=ticker, name=ticker, sector="Materials", asset_class="Equity"
    )


BHP = make_security(1, "BHP")
CBA = make_security(2, "CBA")
VAS = make_security(3, "VAS")


def close(day: int, value: str) -> DailyClose:
    return DailyClose(date(2026, 11, day), Decimal(value))


class FakeProvider:
    """Returns the closes given for each ticker and records every request."""

    def __init__(self, closes: dict[str, list[DailyClose]], failing: tuple[str, ...] = ()):
        self.closes = closes
        self.failing = failing
        self.requests: list[tuple[str, date, date]] = []

    def fetch_closes(self, ticker: str, start: date, end: date) -> list[DailyClose]:
        self.requests.append((ticker, start, end))
        if ticker in self.failing:
            raise ProviderError(f"No data for {ticker}")
        return self.closes.get(ticker, [])


class FakeStore:
    """Stands in for the database and records what was saved."""

    def __init__(self, failing: tuple[str, ...] = ()):
        self.failing = failing
        self.saved: dict[str, list[DailyClose]] = {}

    def save(self, security: Security, closes: list[DailyClose]) -> int:
        if security.ticker in self.failing:
            raise RuntimeError("The database is unavailable")
        self.saved[security.ticker] = closes
        return len(closes)


def refresh(securities, provider, store=None, latest_dates=None) -> RefreshResult:
    store = store or FakeStore()
    return refresh_securities(securities, latest_dates or {}, provider, TODAY, store.save)


# --- Which days to fetch ---


def test_window_starts_a_few_days_before_the_latest_stored_price():
    start, end = refresh_window(date(2026, 11, 10), TODAY, overlap_days=5)

    assert start == date(2026, 11, 5)
    assert end == TODAY


def test_window_reaches_back_to_an_old_latest_price():
    start, _ = refresh_window(date(2026, 8, 1), TODAY, overlap_days=5)

    assert start == date(2026, 7, 27)


def test_window_is_the_full_lookback_when_nothing_is_stored():
    start, end = refresh_window(None, TODAY, lookback_days=365)

    assert start == date(2025, 11, 13)
    assert end == TODAY


# --- Refreshing securities ---


def test_closes_are_fetched_and_saved_for_each_security():
    provider = FakeProvider(
        {"BHP": [close(12, "60.39"), close(13, "58.86")], "CBA": [close(13, "170.87")]}
    )
    store = FakeStore()

    result = refresh([BHP, CBA], provider, store)

    assert result.attempted == 2
    assert result.saved == 3
    assert result.failed == []
    assert store.saved == {
        "BHP": [close(12, "60.39"), close(13, "58.86")],
        "CBA": [close(13, "170.87")],
    }


def test_each_security_is_fetched_for_its_own_window():
    provider = FakeProvider({})

    refresh([BHP, CBA], provider, latest_dates={BHP.id: date(2026, 11, 10)})

    assert provider.requests == [
        ("BHP", date(2026, 11, 5), TODAY),
        ("CBA", date(2025, 11, 13), TODAY),
    ]


def test_no_closes_is_not_a_failure_and_saves_nothing():
    store = FakeStore()

    result = refresh([BHP], FakeProvider({"BHP": []}), store)

    assert result.failed == []
    assert result.saved == 0
    assert store.saved == {}
    assert not result.all_failed


def test_one_provider_failure_does_not_stop_the_others():
    provider = FakeProvider(
        {"BHP": [close(13, "58.86")], "VAS": [close(13, "112.57")]}, failing=("CBA",)
    )
    store = FakeStore()

    result = refresh([BHP, CBA, VAS], provider, store)

    assert result.failed == ["CBA"]
    assert result.saved == 2
    assert set(store.saved) == {"BHP", "VAS"}
    assert not result.all_failed


def test_a_failed_save_counts_as_a_failure_and_the_rest_carry_on():
    provider = FakeProvider({"BHP": [close(13, "58.86")], "CBA": [close(13, "170.87")]})
    store = FakeStore(failing=("BHP",))

    result = refresh([BHP, CBA], provider, store)

    assert result.failed == ["BHP"]
    assert result.saved == 1
    assert set(store.saved) == {"CBA"}


def test_all_failed_is_true_only_when_every_security_fails():
    result = refresh([BHP, CBA], FakeProvider({}, failing=("BHP", "CBA")))

    assert result.failed == ["BHP", "CBA"]
    assert result.all_failed


def test_no_securities_is_not_a_failure():
    result = refresh([], FakeProvider({}))

    assert result.attempted == 0
    assert not result.all_failed
