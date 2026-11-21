"""The seed scripts and the user lookup, run against PostgreSQL."""

from app.models import Role
from app.services.securities import list_securities, security_ids_by_ticker
from app.services.users import find_by_email
from factories import make_user
from scripts.seed import SECURITIES, seed_securities
from scripts.seed_users import seed_users


def test_seeding_securities_twice_adds_nothing_the_second_time(db):
    assert seed_securities(db, SECURITIES) == len(SECURITIES)
    assert seed_securities(db, SECURITIES) == 0

    tickers = [security.ticker for security in list_securities(db)]
    assert tickers == sorted(row["ticker"] for row in SECURITIES)
    assert set(security_ids_by_ticker(db)) == set(tickers)


def test_seeding_a_user_twice_keeps_the_first_password(db):
    user = {
        "email": "analyst@example.com",
        "name": "Demo Analyst",
        "role": Role.ANALYST.value,
        "password_hash": "first hash",
        "is_active": True,
    }

    assert seed_users(db, [user]) == ["analyst@example.com"]
    assert seed_users(db, [{**user, "password_hash": "second hash"}]) == []
    assert find_by_email(db, "analyst@example.com").password_hash == "first hash"


def test_a_user_is_found_whatever_the_capital_letters(db, save):
    save(make_user(Role.OPERATIONS))

    assert find_by_email(db, " Operations@Example.com ").role == Role.OPERATIONS
    assert find_by_email(db, "nobody@example.com") is None
