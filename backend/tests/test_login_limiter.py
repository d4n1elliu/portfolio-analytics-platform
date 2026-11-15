"""Limiting failed sign-ins. No database is used."""

from datetime import UTC, datetime, timedelta

from app.services.login_limiter import LoginLimiter

NOW = datetime(2026, 11, 16, 9, 0, tzinfo=UTC)
ADDRESS = "203.0.113.5"


def limiter_with_failures(count: int, address: str = ADDRESS) -> LoginLimiter:
    limiter = LoginLimiter(max_failures=3, window=timedelta(minutes=15))
    for _ in range(count):
        limiter.record_failure(address, NOW)
    return limiter


def test_new_address_may_try():
    assert limiter_with_failures(0).retry_after(ADDRESS, NOW) is None


def test_address_may_try_while_under_the_limit():
    assert limiter_with_failures(2).retry_after(ADDRESS, NOW) is None


def test_address_is_blocked_at_the_limit():
    assert limiter_with_failures(3).retry_after(ADDRESS, NOW) == timedelta(minutes=15)


def test_wait_shrinks_as_time_passes():
    later = NOW + timedelta(minutes=10)

    assert limiter_with_failures(3).retry_after(ADDRESS, later) == timedelta(minutes=5)


def test_address_may_try_again_after_the_window():
    later = NOW + timedelta(minutes=15)

    assert limiter_with_failures(3).retry_after(ADDRESS, later) is None


def test_one_address_does_not_block_another():
    assert limiter_with_failures(3).retry_after("198.51.100.9", NOW) is None


def test_old_failures_are_forgotten():
    limiter = limiter_with_failures(3)

    limiter.retry_after("198.51.100.9", NOW + timedelta(minutes=15))

    assert limiter._failures == {}
