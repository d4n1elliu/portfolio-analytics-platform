"""Builders for the models that more than one test file needs."""

from datetime import date
from decimal import Decimal

from app.models import Role, Security, Trade, TradeSide, User
from app.services.passwords import hash_password

DEFAULT_TRADE_DATE = date(2026, 3, 16)
# Made up for the tests. Hashed once, because hashing is slow on purpose.
USER_PASSWORD = "a test password"
_USER_PASSWORD_HASH = hash_password(USER_PASSWORD)


def make_security(ticker: str, sector: str = "Materials") -> Security:
    return Security(
        ticker=ticker,
        name=f"{ticker} Limited",
        sector=sector,
        asset_class="Equity",
        currency="AUD",
    )


def buy(
    security: Security,
    quantity: str,
    price: str,
    fees: str = "0",
    on: date = DEFAULT_TRADE_DATE,
) -> Trade:
    return _trade(security, TradeSide.BUY, quantity, price, fees, on)


def sell(
    security: Security,
    quantity: str,
    price: str,
    fees: str = "0",
    on: date = DEFAULT_TRADE_DATE,
) -> Trade:
    return _trade(security, TradeSide.SELL, quantity, price, fees, on)


def _trade(
    security: Security, side: TradeSide, quantity: str, price: str, fees: str, on: date
) -> Trade:
    return Trade(
        security=security,
        trade_date=on,
        side=side,
        quantity=Decimal(quantity),
        price=Decimal(price),
        fees=Decimal(fees),
    )


def make_user(role: Role = Role.ANALYST, user_id: int = 1, is_active: bool = True) -> User:
    """A user who signs in with USER_PASSWORD."""
    return User(
        id=user_id,
        email=f"{role.value}@example.com",
        name=f"Test {role.value}",
        password_hash=_USER_PASSWORD_HASH,
        role=role.value,
        is_active=is_active,
    )
