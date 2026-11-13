"""Unit tests for holdings. No database is used."""

from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models import Security, Trade, TradeSide
from app.schemas.holding import HoldingRead
from app.services.holdings import build_holdings


def make_security(ticker: str, sector: str = "Materials") -> Security:
    return Security(
        ticker=ticker,
        name=f"{ticker} Limited",
        sector=sector,
        asset_class="Equity",
        currency="AUD",
    )


def buy(security: Security, quantity: str, price: str, fees: str = "0") -> Trade:
    return _trade(security, TradeSide.BUY, quantity, price, fees)


def sell(security: Security, quantity: str, price: str, fees: str = "0") -> Trade:
    return _trade(security, TradeSide.SELL, quantity, price, fees)


def _trade(security: Security, side: TradeSide, quantity: str, price: str, fees: str) -> Trade:
    return Trade(
        security=security,
        trade_date=date(2026, 3, 16),
        side=side,
        quantity=Decimal(quantity),
        price=Decimal(price),
        fees=Decimal(fees),
    )


def tickers(holdings) -> list[str]:
    return [holding.security.ticker for holding in holdings]


# --- Building holdings from trades ---


def test_no_trades_gives_no_holdings():
    assert build_holdings([], include_closed=False) == []


def test_each_security_gets_its_own_position_ordered_by_ticker():
    cba, bhp = make_security("CBA"), make_security("BHP")
    trades = [buy(cba, "10", "150"), buy(bhp, "100", "40"), buy(cba, "5", "160")]

    holdings = build_holdings(trades, include_closed=False)

    assert tickers(holdings) == ["BHP", "CBA"]
    assert holdings[0].position.quantity == 100
    assert holdings[1].position.quantity == 15


def test_closed_positions_are_left_out_by_default():
    bhp, cba = make_security("BHP"), make_security("CBA")
    trades = [buy(bhp, "100", "40"), buy(cba, "10", "150"), sell(cba, "10", "160")]

    assert tickers(build_holdings(trades, include_closed=False)) == ["BHP"]


def test_closed_positions_are_returned_when_asked_for():
    bhp, cba = make_security("BHP"), make_security("CBA")
    trades = [buy(bhp, "100", "40"), buy(cba, "10", "150"), sell(cba, "10", "160")]

    holdings = build_holdings(trades, include_closed=True)

    assert tickers(holdings) == ["BHP", "CBA"]
    assert holdings[1].position.realised_pnl == 100


def test_oversold_position_is_always_returned():
    bhp = make_security("BHP")
    trades = [buy(bhp, "100", "40"), sell(bhp, "150", "45")]

    holdings = build_holdings(trades, include_closed=False)

    assert tickers(holdings) == ["BHP"]
    assert holdings[0].position.oversold_quantity == 50


# --- Response shape ---


def test_response_rounds_money_to_cents_and_average_cost_to_six_places():
    bhp = make_security("BHP")
    trades = [
        buy(bhp, "400", "41.85", fees="29.95"),
        buy(bhp, "200", "43.10", fees="19.95"),
        sell(bhp, "250", "45.72", fees="29.95"),
    ]

    holding = HoldingRead.from_holding(build_holdings(trades, include_closed=False)[0])

    assert holding.ticker == "BHP"
    assert holding.security_name == "BHP Limited"
    assert holding.quantity == 350
    assert str(holding.average_cost) == "42.349833"
    assert str(holding.cost_basis) == "14822.44"
    assert str(holding.realised_pnl) == "812.59"


def test_response_has_no_average_cost_for_a_closed_position():
    cba = make_security("CBA")
    trades = [buy(cba, "10", "150"), sell(cba, "10", "160")]

    holding = HoldingRead.from_holding(build_holdings(trades, include_closed=True)[0])

    assert holding.average_cost is None
    assert str(holding.cost_basis) == "0.00"


# --- Endpoint ---


class FakeSession:
    """Stands in for the database session and returns the given trades."""

    def __init__(self, trades: list[Trade]):
        self.trades = trades

    def scalars(self, statement):
        return self.trades


@pytest.fixture
def client_with_trades():
    def make_client(trades: list[Trade]) -> TestClient:
        app.dependency_overrides[get_db] = lambda: FakeSession(trades)
        return TestClient(app)

    yield make_client
    app.dependency_overrides.clear()


def test_endpoint_returns_open_positions(client_with_trades):
    bhp, cba = make_security("BHP"), make_security("CBA", sector="Financials")
    trades = [buy(bhp, "100", "40", fees="20"), buy(cba, "10", "150"), sell(cba, "10", "160")]

    response = client_with_trades(trades).get("/holdings")

    assert response.status_code == 200
    assert response.json() == [
        {
            "ticker": "BHP",
            "security_name": "BHP Limited",
            "sector": "Materials",
            "asset_class": "Equity",
            "currency": "AUD",
            "quantity": "100",
            "average_cost": "40.200000",
            "cost_basis": "4020.00",
            "realised_pnl": "0.00",
            "oversold_quantity": "0",
        }
    ]


def test_endpoint_includes_closed_positions_when_asked(client_with_trades):
    bhp, cba = make_security("BHP"), make_security("CBA", sector="Financials")
    trades = [buy(bhp, "100", "40"), buy(cba, "10", "150"), sell(cba, "10", "160")]

    response = client_with_trades(trades).get("/holdings", params={"include_closed": "true"})

    assert [holding["ticker"] for holding in response.json()] == ["BHP", "CBA"]
    assert response.json()[1]["average_cost"] is None
