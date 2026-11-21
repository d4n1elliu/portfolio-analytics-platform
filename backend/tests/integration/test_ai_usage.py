"""Recording AI usage and reading what is left, with PostgreSQL behind it."""

from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException

from app.ai.usage import read_allowance, record_usage
from app.models import Role
from app.routes.dependencies import require_ai_allowance
from factories import make_user, sign_in

NOW = datetime(2026, 11, 21, 12, 0, tzinfo=UTC)


@pytest.fixture
def user(save):
    return save(make_user(Role.ANALYST))


def test_requests_count_for_an_hour_and_tokens_for_a_day(db, user):
    record_usage(db, user, 1000, 500, NOW - timedelta(hours=25))
    record_usage(db, user, 100, 50, NOW - timedelta(hours=2))
    record_usage(db, user, 10, 5, NOW - timedelta(minutes=5))

    allowance = read_allowance(db, user, NOW)

    assert allowance.requests_used == 1
    assert allowance.tokens_used == 165


def test_one_user_does_not_use_up_the_allowance_of_another(db, save, user):
    other = save(make_user(Role.OPERATIONS, user_id=2))
    record_usage(db, other, 100, 50, NOW)

    assert read_allowance(db, user, NOW).requests_used == 0
    assert read_allowance(db, other, NOW).tokens_used == 150


def test_a_user_with_no_usage_has_used_nothing(db, user):
    allowance = read_allowance(db, user, NOW)

    assert (allowance.requests_used, allowance.tokens_used) == (0, 0)
    assert allowance.limit_reached is None


def test_a_request_past_the_limit_is_refused(db, user):
    for _ in range(20):
        record_usage(db, user, 1, 1, NOW)
    allowance = read_allowance(db, user, NOW)

    with pytest.raises(HTTPException) as refused:
        require_ai_allowance(allowance)

    assert refused.value.status_code == 429
    assert refused.value.detail == "You have reached the limit of 20 AI requests an hour."


def test_the_endpoint_reports_the_usage_of_the_signed_in_user(
    db, user, client_with_session, monkeypatch
):
    monkeypatch.setattr("app.routes.dependencies.AI_ENABLED", True)
    record_usage(db, user, 100, 50, datetime.now(UTC))
    client = client_with_session(db)
    sign_in(client, Role.ANALYST)

    assert client.get("/ai/usage").json() == {
        "requests_used": 1,
        "requests_limit": 20,
        "tokens_used": 150,
        "tokens_limit": 200000,
    }
