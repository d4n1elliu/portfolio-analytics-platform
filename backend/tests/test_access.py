"""Which endpoints need a sign in. No database is used."""

import pytest

from app.models import Role
from factories import make_user, sign_in

READ_ENDPOINTS = [
    "/holdings",
    "/portfolio/history",
    "/portfolio/performance",
    "/securities",
    "/trades",
    "/trades/export",
    "/trades/imports",
]
OPEN_ENDPOINTS = ["/health", "/docs"]

NOT_SIGNED_IN = {"detail": "Sign in to continue."}


def client_signed_in_as(client_with_users, role: Role):
    """Sign in through the login endpoint, so the real session check is used."""
    client = client_with_users(make_user(role))
    sign_in(client, role)
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


# --- POST /trades/import ---

NOT_A_CSV = {"file": ("trades.txt", b"not a csv", "text/plain")}


def test_importing_needs_a_sign_in(client_with_users):
    response = client_with_users(make_user()).post("/trades/import", files=NOT_A_CSV)

    assert response.status_code == 401
    assert response.json() == NOT_SIGNED_IN


@pytest.mark.parametrize("role", [Role.PORTFOLIO_MANAGER, Role.ANALYST])
def test_roles_other_than_operations_cannot_import(client_with_users, role):
    response = client_signed_in_as(client_with_users, role).post("/trades/import", files=NOT_A_CSV)

    assert response.status_code == 403
    assert response.json() == {"detail": "Your role does not allow this."}


def test_operations_can_import(client_with_users):
    client = client_signed_in_as(client_with_users, Role.OPERATIONS)

    response = client.post("/trades/import", files=NOT_A_CSV)

    # Past the role check: the file itself is what is refused.
    assert response.status_code == 400
    assert response.json() == {"detail": "The file must be a .csv file."}


def test_import_is_refused_before_the_file_is_looked_at(client_with_users):
    client = client_signed_in_as(client_with_users, Role.ANALYST)

    assert client.post("/trades/import").status_code == 403
