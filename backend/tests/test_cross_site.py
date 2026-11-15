"""Refusing requests from other sites that change data. No database is used."""

import pytest

from app.config import CORS_ORIGINS
from factories import USER_PASSWORD, make_user

ALLOWED_SITE = CORS_ORIGINS[0]
OTHER_SITE = "https://evil.example"
CREDENTIALS = {"email": "analyst@example.com", "password": USER_PASSWORD}


def test_sign_in_from_another_site_is_refused(client_with_users):
    client = client_with_users(make_user())

    response = client.post("/auth/login", json=CREDENTIALS, headers={"origin": OTHER_SITE})

    assert response.status_code == 403
    assert "set-cookie" not in response.headers


def test_sign_in_from_the_app_is_allowed(client_with_users):
    client = client_with_users(make_user())

    response = client.post("/auth/login", json=CREDENTIALS, headers={"origin": ALLOWED_SITE})

    assert response.status_code == 200


def test_request_with_no_origin_is_allowed(client_with_users):
    assert client_with_users(make_user()).post("/auth/login", json=CREDENTIALS).status_code == 200


@pytest.mark.parametrize("path", ["/auth/logout", "/trades/import"])
def test_other_changes_from_another_site_are_refused(client_with_users, path):
    response = client_with_users(make_user()).post(path, headers={"origin": OTHER_SITE})

    assert response.status_code == 403


def test_reading_from_another_site_is_not_refused_here(client_with_users):
    response = client_with_users(make_user()).get("/health", headers={"origin": OTHER_SITE})

    assert response.status_code == 200


def test_the_app_may_read_how_long_to_wait(client_with_users):
    client = client_with_users(make_user())

    response = client.post("/auth/login", json=CREDENTIALS, headers={"origin": ALLOWED_SITE})

    assert response.headers["access-control-expose-headers"] == "Retry-After"
