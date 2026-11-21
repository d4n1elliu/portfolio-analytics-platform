"""The rules the database enforces itself, whichever code inserts the row."""

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Price, Role
from factories import buy, make_security, make_user

DAY = date(2026, 11, 13)


def changed(row, change: dict):
    for column, value in change.items():
        setattr(row, column, value)
    return row


def test_two_securities_cannot_share_a_ticker(save):
    save(make_security("BHP"))

    with pytest.raises(IntegrityError):
        save(make_security("BHP"))


@pytest.mark.parametrize(
    "change",
    [
        {"side": "HOLD"},
        {"quantity": Decimal("0")},
        {"price": Decimal("0")},
        {"fees": Decimal("-1")},
    ],
    ids=["unknown side", "zero quantity", "zero price", "negative fees"],
)
def test_an_invalid_trade_is_rejected(save, change):
    trade = changed(buy(save(make_security("BHP")), "10", "40"), change)

    with pytest.raises(IntegrityError):
        save(trade)


def test_a_security_has_one_price_per_day(save):
    security = save(make_security("BHP"))
    save(Price(security=security, price_date=DAY, close=Decimal("40")))

    with pytest.raises(IntegrityError):
        save(Price(security=security, price_date=DAY, close=Decimal("41")))


def test_a_price_must_be_above_zero(save):
    security = save(make_security("BHP"))

    with pytest.raises(IntegrityError):
        save(Price(security=security, price_date=DAY, close=Decimal("0")))


@pytest.mark.parametrize(
    "change",
    [{"role": "admin"}, {"email": "Analyst@Example.com"}],
    ids=["unknown role", "capital letters in the email"],
)
def test_an_invalid_user_is_rejected(save, change):
    user = changed(make_user(), change)

    with pytest.raises(IntegrityError):
        save(user)


def test_two_users_cannot_share_an_email(save):
    save(make_user(Role.ANALYST, user_id=1))

    with pytest.raises(IntegrityError):
        save(make_user(Role.ANALYST, user_id=2))
