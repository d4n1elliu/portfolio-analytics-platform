"""Ending sessions and changing a password, with PostgreSQL behind them."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select

from app.models import Role, UserSession
from app.routes.dependencies import SESSION_COOKIE
from app.services.tokens import create_token
from app.services.user_sessions import start_session
from factories import USER_PASSWORD, make_user, sign_in

NEW_PASSWORD = "a new test password"


@pytest.fixture
def user(save):
    return save(make_user(Role.ANALYST))


@pytest.fixture
def signed_in(db, user, client_with_session):
    def new_client():
        client = client_with_session(db)
        sign_in(client, Role.ANALYST)
        return client

    return new_client


def is_signed_in(client) -> bool:
    return client.get("/auth/me").status_code == 200


def log_in(client, password: str):
    return client.post("/auth/login", json={"email": "analyst@example.com", "password": password})


def test_a_copied_cookie_stops_working_after_sign_out(signed_in):
    client = signed_in()
    copied = client.cookies[SESSION_COOKIE]

    client.post("/auth/logout")
    client.cookies.set(SESSION_COOKIE, copied)

    assert not is_signed_in(client)


def test_signing_out_leaves_the_other_sessions_of_the_user(signed_in):
    laptop, phone = signed_in(), signed_in()

    laptop.post("/auth/logout")

    assert is_signed_in(phone)


def test_a_session_past_its_end_is_refused_even_with_a_fresh_token(db, user, client_with_session):
    now = datetime.now(UTC)
    old_session = start_session(db, user, now - timedelta(days=2))
    client = client_with_session(db)
    client.cookies.set(SESSION_COOKIE, create_token(old_session.id, now))

    assert not is_signed_in(client)


def test_changing_the_password_signs_out_everywhere_else(signed_in):
    laptop, phone = signed_in(), signed_in()

    response = laptop.post(
        "/auth/password", json={"current_password": USER_PASSWORD, "new_password": NEW_PASSWORD}
    )

    assert response.status_code == 204
    assert is_signed_in(laptop)
    assert not is_signed_in(phone)
    assert log_in(phone, USER_PASSWORD).status_code == 401
    assert log_in(phone, NEW_PASSWORD).status_code == 200


def test_signing_in_clears_out_the_sessions_that_have_expired(db, user, signed_in):
    start_session(db, user, datetime.now(UTC) - timedelta(days=2))

    signed_in()

    assert db.scalar(select(func.count()).select_from(UserSession)) == 1
