"""Building the demo accounts. No database is used."""

import pytest

from app.models import Role
from app.services.passwords import MIN_PASSWORD_LENGTH, verify_password
from scripts.seed_users import (
    SeedError,
    build_demo_users,
    main,
    password_variable,
)

PASSWORDS = {password_variable(role): f"demo password for {role.value}" for role in Role}


def test_one_account_is_built_for_each_role():
    users = build_demo_users(PASSWORDS)

    assert sorted(user["role"] for user in users) == sorted(role.value for role in Role)


def test_each_account_gets_its_own_password():
    for user in build_demo_users(PASSWORDS):
        password = PASSWORDS[password_variable(Role(user["role"]))]

        assert verify_password(password, user["password_hash"])


def test_the_password_itself_is_not_in_the_row():
    for user in build_demo_users(PASSWORDS):
        assert not set(PASSWORDS.values()) & set(user.values())


def test_emails_are_lowercase_and_different():
    emails = [user["email"] for user in build_demo_users(PASSWORDS)]

    assert emails == [email.lower() for email in emails]
    assert len(set(emails)) == len(emails)


def test_accounts_are_active():
    assert all(user["is_active"] for user in build_demo_users(PASSWORDS))


def test_missing_password_is_named_in_the_error():
    variable = password_variable(Role.ANALYST)
    passwords = {name: value for name, value in PASSWORDS.items() if name != variable}

    with pytest.raises(SeedError, match=variable):
        build_demo_users(passwords)


def test_short_password_is_rejected():
    variable = password_variable(Role.OPERATIONS)
    passwords = {**PASSWORDS, variable: "x" * (MIN_PASSWORD_LENGTH - 1)}

    with pytest.raises(SeedError, match=variable):
        build_demo_users(passwords)


def test_every_missing_password_is_reported_at_once():
    with pytest.raises(SeedError) as error:
        build_demo_users({})

    for role in Role:
        assert password_variable(role) in str(error.value)


def test_main_saves_nothing_when_a_password_is_missing(capsys):
    assert main({}) == 1
    assert "Nothing was saved" in capsys.readouterr().out
