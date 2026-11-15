"""Which endpoints need a sign in. No database is used."""

import pytest

from app.models import Role
from factories import USER_PASSWORD, make_user

READ_ENDPOINTS = ["/holdings", "/portfolio/history", "/securities", "/trades"]
OPEN_ENDPOINTS = ["/health", "/docs"]

NOT_SIGNED_IN = {"detail": "Sign in to continue."}


def client_signed_in_as(client_with_users, role: Role):
    """Sign in through the login endpoint, so the real session check is used."""
    client = client_with_users(make_user(role))
    response = client.post(
        "/auth/login", json={"email": f"{role.value}@example.com", "password": USER_PASSWORD}
    )
    assert response.status_code == 200
    return client


@pytest.mark.parametrize("path", READ_ENDPOINTS)
def test_reading_data_needs_a_sign_in(client_with_users, path):
    response = client_with_users(make_user()).get(path)

    assert response.status_code == 401
    assert response.json() == NOT_SIGNED_IN


@pytest.mark.parametrize("path", READ_ENDPOINTS)
@pytest.mark.parametrize("role", list(Role))
def test_every_role_can_read_data(client_with_users, role, path):
    assert client_signed_in_as(client_with_users, role).get(path).status_code == 200


@pytest.mark.parametrize("path", OPEN_ENDPOINTS)
def test_health_and_docs_need_no_sign_in(client_with_users, path):
    assert client_with_users(make_user()).get(path).status_code == 200


def test_signing_in_needs_no_sign_in(client_with_users):
    client = client_with_users(make_user())

    response = client.post("/auth/login", json={"email": "x@example.com", "password": "x"})

    assert response.json() == {"detail": "Incorrect email or password."}


def test_database_health_check_needs_no_sign_in(client_with_users):
    """The deploy calls it without signing in."""
    assert client_with_users(make_user()).get("/health/db").status_code == 200
