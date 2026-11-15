"""Signing in and out. No database is used."""

from datetime import UTC, datetime, timedelta

import pytest

from app.models import Role
from app.routes.dependencies import SESSION_COOKIE
from app.services.login_limiter import MAX_FAILURES
from app.services.tokens import create_token
from app.services.users import check_credentials
from factories import USER_PASSWORD, make_user

NOT_SIGNED_IN = {"detail": "Sign in to continue."}
WRONG_DETAILS = {"detail": "Incorrect email or password."}


def sign_in(client, email="analyst@example.com", password=USER_PASSWORD):
    return client.post("/auth/login", json={"email": email, "password": password})


def session_cookie_header(response) -> str:
    return response.headers["set-cookie"].lower()


# --- Checking a password ---


def test_right_password_gives_the_user():
    user = make_user()

    assert check_credentials(user, USER_PASSWORD) is user


def test_wrong_password_gives_nothing():
    assert check_credentials(make_user(), "wrong password") is None


def test_unknown_email_gives_nothing():
    assert check_credentials(None, USER_PASSWORD) is None


def test_inactive_user_gives_nothing_even_with_the_right_password():
    assert check_credentials(make_user(is_active=False), USER_PASSWORD) is None


# --- POST /auth/login ---


def test_sign_in_returns_the_user_without_the_password_hash(client_with_users):
    response = sign_in(client_with_users(make_user(Role.ANALYST)))

    assert response.status_code == 200
    assert response.json() == {
        "email": "analyst@example.com",
        "name": "Test analyst",
        "role": "analyst",
    }


def test_sign_in_sets_a_cookie_that_page_scripts_cannot_read(client_with_users):
    cookie = session_cookie_header(sign_in(client_with_users(make_user())))

    assert cookie.startswith(f"{SESSION_COOKIE}=")
    assert "httponly" in cookie
    assert "samesite=lax" in cookie
    assert "max-age=28800" in cookie


def test_email_ignores_capital_letters_and_outer_spaces(client_with_users):
    response = sign_in(client_with_users(make_user()), email="  Analyst@Example.com ")

    assert response.status_code == 200


def test_wrong_password_is_rejected(client_with_users):
    response = sign_in(client_with_users(make_user()), password="wrong password")

    assert response.status_code == 401
    assert response.json() == WRONG_DETAILS
    assert "set-cookie" not in response.headers


def test_unknown_email_gets_the_same_answer_as_a_wrong_password(client_with_users):
    response = sign_in(client_with_users(make_user()), email="nobody@example.com")

    assert response.status_code == 401
    assert response.json() == WRONG_DETAILS


def test_inactive_user_gets_the_same_answer_as_a_wrong_password(client_with_users):
    response = sign_in(client_with_users(make_user(is_active=False)))

    assert response.status_code == 401
    assert response.json() == WRONG_DETAILS


@pytest.mark.parametrize("body", [{}, {"email": "analyst@example.com"}, {"password": "x"}])
def test_missing_email_or_password_is_rejected(client_with_users, body):
    response = client_with_users(make_user()).post("/auth/login", json=body)

    assert response.status_code == 422


def test_too_many_failed_sign_ins_are_blocked(client_with_users):
    client = client_with_users(make_user())
    for _ in range(MAX_FAILURES):
        assert sign_in(client, password="wrong password").status_code == 401

    response = sign_in(client)

    assert response.status_code == 429
    assert response.json() == {"detail": "Too many failed sign-ins. Try again in 15 minutes."}
    assert int(response.headers["retry-after"]) > 0


def test_failed_sign_ins_are_counted_for_each_visitor(client_with_users):
    client = client_with_users(make_user())
    for _ in range(MAX_FAILURES):
        client.post(
            "/auth/login",
            json={"email": "analyst@example.com", "password": "wrong password"},
            headers={"x-forwarded-for": "203.0.113.5"},
        )

    response = client.post(
        "/auth/login",
        json={"email": "analyst@example.com", "password": USER_PASSWORD},
        headers={"x-forwarded-for": "198.51.100.9"},
    )

    assert response.status_code == 200


def test_a_successful_sign_in_does_not_clear_the_failures(client_with_users):
    client = client_with_users(make_user())
    for _ in range(MAX_FAILURES - 1):
        sign_in(client, password="wrong password")
    assert sign_in(client).status_code == 200

    sign_in(client, password="wrong password")

    assert sign_in(client).status_code == 429


# --- GET /auth/me ---


def test_signed_in_user_is_returned(client_with_users):
    client = client_with_users(make_user(Role.OPERATIONS))
    sign_in(client, email="operations@example.com")

    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["role"] == "operations"


def test_no_session_is_rejected(client_with_users):
    response = client_with_users(make_user()).get("/auth/me")

    assert response.status_code == 401
    assert response.json() == NOT_SIGNED_IN


def test_expired_session_is_rejected(client_with_users):
    client = client_with_users(make_user(user_id=1))
    long_ago = datetime.now(UTC) - timedelta(days=1)
    client.cookies.set(SESSION_COOKIE, create_token(1, long_ago))

    assert client.get("/auth/me").status_code == 401


def test_tampered_session_is_rejected(client_with_users):
    client = client_with_users(make_user(user_id=1))
    token = create_token(1, datetime.now(UTC))
    client.cookies.set(SESSION_COOKIE, token[:-2] + ("aa" if token[-2:] != "aa" else "bb"))

    assert client.get("/auth/me").status_code == 401


def test_session_of_a_user_who_no_longer_exists_is_rejected(client_with_users):
    client = client_with_users(make_user(user_id=1))
    client.cookies.set(SESSION_COOKIE, create_token(99, datetime.now(UTC)))

    assert client.get("/auth/me").status_code == 401


def test_session_of_a_user_made_inactive_is_rejected(client_with_users):
    client = client_with_users(make_user(user_id=1, is_active=False))
    client.cookies.set(SESSION_COOKIE, create_token(1, datetime.now(UTC)))

    assert client.get("/auth/me").status_code == 401


# --- POST /auth/logout ---


def test_sign_out_clears_the_session(client_with_users):
    client = client_with_users(make_user())
    sign_in(client)

    response = client.post("/auth/logout")

    assert response.status_code == 204
    assert f'{SESSION_COOKIE}=""' in session_cookie_header(response)
    assert client.get("/auth/me").status_code == 401


def test_sign_out_works_when_not_signed_in(client_with_users):
    assert client_with_users(make_user()).post("/auth/logout").status_code == 204
