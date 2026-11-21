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
    "/trades/imports",
]
SECURITY_ENDPOINTS = ["/holdings/BHP", "/securities/BHP/prices"]
OPEN_ENDPOINTS = ["/health", "/docs"]

NOT_SIGNED_IN = {"detail": "Sign in to continue."}


def client_signed_in_as(client_with_users, role: Role):
    """Sign in through the login endpoint, so the real session check is used."""
    client = client_with_users(make_user(role))
    sign_in(client, role)
    return client


@pytest.mark.parametrize("path", [*READ_ENDPOINTS, *SECURITY_ENDPOINTS, "/trades/export"])
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


# --- AI endpoints ---


def test_ai_endpoints_need_a_sign_in(client_with_users, monkeypatch):
    monkeypatch.setattr("app.routes.dependencies.AI_ENABLED", True)

    response = client_with_users(make_user()).get("/ai/usage")

    assert response.status_code == 401
    assert response.json() == NOT_SIGNED_IN


def test_asking_the_assistant_needs_a_sign_in(client_with_users, monkeypatch):
    monkeypatch.setattr("app.routes.dependencies.AI_ENABLED", True)
    question = {"question": "What do I hold?"}

    response = client_with_users(make_user()).post("/ai/chat", json=question)

    assert response.status_code == 401
    assert response.json() == NOT_SIGNED_IN


@pytest.mark.parametrize("path", ["/research/documents", "/research/documents/1"])
def test_reading_research_needs_a_sign_in(client_with_users, monkeypatch, path):
    monkeypatch.setattr("app.routes.dependencies.AI_ENABLED", True)

    assert client_with_users(make_user()).get(path).status_code == 401


def test_research_is_not_found_while_the_ai_features_are_off(client_with_users):
    client = client_signed_in_as(client_with_users, Role.ANALYST)

    assert client.get("/research/documents").status_code == 404


def test_ai_endpoints_are_not_found_while_the_ai_features_are_off(client_with_users):
    response = client_signed_in_as(client_with_users, Role.ANALYST).get("/ai/usage")

    assert response.status_code == 404
    assert response.json() == {"detail": "The AI features are not turned on."}


@pytest.mark.parametrize("role", list(Role))
def test_every_role_can_read_its_ai_usage(client_with_users, monkeypatch, role):
    monkeypatch.setattr("app.routes.dependencies.AI_ENABLED", True)

    response = client_signed_in_as(client_with_users, role).get("/ai/usage")

    assert response.status_code == 200
    assert response.json() == {
        "requests_used": 0,
        "requests_limit": 20,
        "tokens_used": 0,
        "tokens_limit": 200000,
    }


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


# --- GET /trades/export ---


@pytest.mark.parametrize("role", [Role.OPERATIONS, Role.PORTFOLIO_MANAGER])
def test_operations_and_portfolio_managers_can_export(client_with_users, role):
    assert client_signed_in_as(client_with_users, role).get("/trades/export").status_code == 200


def test_an_analyst_cannot_export(client_with_users):
    response = client_signed_in_as(client_with_users, Role.ANALYST).get("/trades/export")

    assert response.status_code == 403
    assert response.json() == {"detail": "Your role does not allow this."}
