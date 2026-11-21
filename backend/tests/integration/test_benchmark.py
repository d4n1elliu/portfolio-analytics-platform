"""The benchmark on the performance endpoint, with PostgreSQL behind it."""

from datetime import date

import pytest

from app.models import Role
from factories import buy, closes, make_security, make_user, sign_in

MONDAY = date(2026, 11, 9)
TUESDAY = date(2026, 11, 10)


@pytest.fixture
def client(db, save, client_with_session):
    bhp = save(make_security("BHP"))
    save(buy(bhp, "100", "10", on=MONDAY), *closes(bhp, {MONDAY: "10", TUESDAY: "12"}))
    save(make_user(Role.ANALYST))
    client = client_with_session(db)
    sign_in(client, Role.ANALYST)
    return client


def test_the_benchmark_return_comes_from_the_stored_prices_of_vas(client, save):
    save(*closes(save(make_security("VAS")), {MONDAY: "100", TUESDAY: "105"}))

    performance = client.get("/portfolio/performance").json()

    assert performance["benchmark"] == "VAS"
    assert performance["periods"][-1]["portfolio_return"] == "0.200000"
    assert performance["periods"][-1]["benchmark_return"] == "0.050000"
    assert [point["benchmark"] for point in performance["growth"]] == ["1.000000", "1.050000"]


def test_there_is_no_benchmark_when_vas_is_not_a_security(client):
    performance = client.get("/portfolio/performance").json()

    assert performance["benchmark"] is None
    assert performance["periods"][-1]["benchmark_return"] is None
    assert performance["growth"][0]["benchmark"] is None


def test_there_is_no_benchmark_when_vas_has_no_prices(client, save):
    save(make_security("VAS"))

    assert client.get("/portfolio/performance").json()["benchmark"] is None
