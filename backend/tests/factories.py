"""Builders for the models that more than one test file needs."""

import io
from datetime import date
from decimal import Decimal

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from app.models import Price, Role, Security, Trade, TradeSide, User
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


def sign_in(client, role: Role) -> None:
    """Sign in through the login endpoint as the user make_user builds for the role."""
    response = client.post(
        "/auth/login", json={"email": f"{role.value}@example.com", "password": USER_PASSWORD}
    )
    assert response.status_code == 200


def closes(security: Security, by_date: dict[date, str]) -> list[Price]:
    """Closing prices for one security, from a date-to-price mapping."""
    return [
        Price(security=security, price_date=day, close=Decimal(close))
        for day, close in by_date.items()
    ]


def make_pdf(text: str) -> bytes:
    writer = PdfWriter()
    page = writer.add_blank_page(width=300, height=144)
    content = DecodedStreamObject()
    content.set_data(f"BT /F1 12 Tf 20 100 Td ({text}) Tj ET".encode())
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    fonts = DictionaryObject({NameObject("/F1"): writer._add_object(font)})
    page[NameObject("/Contents")] = writer._add_object(content)
    page[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): fonts})
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()
