"""Which demo sign-in details are shown to visitors. No database is used."""

from app.models import Role
from app.services.demo_accounts import list_demo_access, password_variable

PASSWORDS = {password_variable(role): f"demo password for {role.value}" for role in Role}


def access_for(role: Role, environ=PASSWORDS):
    return next(access for access in list_demo_access(environ) if access.role is role)


def test_every_role_is_listed():
    assert [access.role for access in list_demo_access({})] == [
        Role.OPERATIONS,
        Role.PORTFOLIO_MANAGER,
        Role.ANALYST,
    ]


def test_read_only_roles_show_their_email_and_password():
    for role in (Role.PORTFOLIO_MANAGER, Role.ANALYST):
        access = access_for(role)

        assert access.email is not None
        assert access.password == PASSWORDS[password_variable(role)]


def test_operations_details_are_never_shown_even_when_its_password_is_set():
    access = access_for(Role.OPERATIONS)

    assert access.email is None
    assert access.password is None


def test_a_role_with_no_password_set_shows_nothing():
    access = access_for(Role.ANALYST, environ={})

    assert access.email is None
    assert access.password is None


def test_an_empty_password_counts_as_not_set():
    access = access_for(Role.ANALYST, environ={password_variable(Role.ANALYST): ""})

    assert access.email is None
    assert access.password is None


def test_endpoint_needs_no_sign_in(client_with_users, monkeypatch):
    for name, value in PASSWORDS.items():
        monkeypatch.setenv(name, value)

    response = client_with_users().get("/auth/demo-accounts")

    assert response.status_code == 200
    assert response.json() == [
        {"role": "operations", "email": None, "password": None},
        {
            "role": "portfolio_manager",
            "email": "pm@example.com",
            "password": "demo password for portfolio_manager",
        },
        {
            "role": "analyst",
            "email": "analyst@example.com",
            "password": "demo password for analyst",
        },
    ]


def test_endpoint_shows_nothing_when_no_password_is_set(client_with_users, monkeypatch):
    for name in PASSWORDS:
        monkeypatch.delenv(name, raising=False)

    response = client_with_users().get("/auth/demo-accounts")

    assert {access["password"] for access in response.json()} == {None}
