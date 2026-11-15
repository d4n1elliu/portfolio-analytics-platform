"""Builders for the models that more than one test file needs."""

from datetime import date
from decimal import Decimal

from app.models import Security, Trade, TradeSide

DEFAULT_TRADE_DATE = date(2026, 3, 16)


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
