"""Unit tests for holdings. No database is used."""

from datetime import date
from decimal import Decimal

from app.models import Price, Security
from app.schemas.holding import HoldingRead
from app.services.holdings import build_holdings
from factories import buy, make_security, sell

PRICE_DATE = date(2026, 11, 13)


def price(security: Security, close: str) -> Price:
    return Price(security=security, price_date=PRICE_DATE, close=Decimal(close))


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


# --- Valuing holdings ---


def test_open_position_with_a_price_is_valued():
    bhp = make_security("BHP")
    trades = [buy(bhp, "100", "40")]

    holding = build_holdings(trades, include_closed=False, prices={"BHP": price(bhp, "46")})[0]

    assert holding.valuation.last_price == 46
    assert holding.valuation.price_date == PRICE_DATE
    assert holding.valuation.market_value == 4600
    assert holding.valuation.unrealised_pnl == 600
    assert holding.weight == 1


def test_position_without_a_price_has_no_valuation_or_weight():
    bhp = make_security("BHP")

    holding = build_holdings([buy(bhp, "100", "40")], include_closed=False)[0]

    assert holding.valuation is None
    assert holding.weight is None


def test_closed_position_is_not_valued_even_with_a_price():
    cba = make_security("CBA")
    trades = [buy(cba, "10", "150"), sell(cba, "10", "160")]

    holding = build_holdings(trades, include_closed=True, prices={"CBA": price(cba, "165")})[0]

    assert holding.valuation is None
    assert holding.weight is None


def test_weights_are_each_market_value_over_the_total():
    bhp, cba = make_security("BHP"), make_security("CBA")
    trades = [buy(bhp, "100", "40"), buy(cba, "10", "150")]
    prices = {"BHP": price(bhp, "30"), "CBA": price(cba, "100")}

    holdings = build_holdings(trades, include_closed=False, prices=prices)

    # BHP is worth 3,000 and CBA 1,000.
    assert holdings[0].weight == Decimal("0.75")
    assert holdings[1].weight == Decimal("0.25")


def test_unpriced_holding_is_left_out_of_the_weights():
    bhp, cba = make_security("BHP"), make_security("CBA")
    trades = [buy(bhp, "100", "40"), buy(cba, "10", "150")]

    holdings = build_holdings(trades, include_closed=False, prices={"BHP": price(bhp, "30")})

    assert holdings[0].weight == 1
    assert holdings[1].weight is None


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


def test_response_rounds_valuation_money_to_cents_and_fractions_to_six_places():
    bhp, cba = make_security("BHP"), make_security("CBA")
    trades = [
        buy(bhp, "400", "41.85", fees="29.95"),
        buy(bhp, "200", "43.10", fees="19.95"),
        sell(bhp, "250", "45.72", fees="29.95"),
        buy(cba, "110", "155.353788"),
    ]
    prices = {"BHP": price(bhp, "46.10"), "CBA": price(cba, "158")}

    holding = HoldingRead.from_holding(build_holdings(trades, include_closed=False, prices=prices)[0])

    assert str(holding.last_price) == "46.10"
    assert holding.price_date == PRICE_DATE
    assert str(holding.market_value) == "16135.00"
    assert str(holding.unrealised_pnl) == "1312.56"
    assert str(holding.unrealised_return) == "0.088552"
    assert str(holding.weight) == "0.481426"


def test_response_has_no_valuation_fields_without_a_price():
    bhp = make_security("BHP")

    holding = HoldingRead.from_holding(build_holdings([buy(bhp, "100", "40")], include_closed=False)[0])

    assert holding.last_price is None
    assert holding.price_date is None
    assert holding.market_value is None
    assert holding.unrealised_pnl is None
    assert holding.unrealised_return is None
    assert holding.weight is None


# --- Endpoint ---


def test_endpoint_returns_open_positions(client_with_data):
    bhp, cba = make_security("BHP"), make_security("CBA", sector="Financials")
    trades = [buy(bhp, "100", "40", fees="20"), buy(cba, "10", "150"), sell(cba, "10", "160")]

    response = client_with_data(trades).get("/holdings")

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
            "last_price": None,
            "price_date": None,
            "market_value": None,
            "unrealised_pnl": None,
            "unrealised_return": None,
            "weight": None,
        }
    ]


def test_endpoint_returns_the_valuation_when_a_price_is_stored(client_with_data):
    bhp = make_security("BHP")
    trades = [buy(bhp, "100", "40", fees="20")]

    response = client_with_data(trades, [price(bhp, "46")]).get("/holdings")

    holding = response.json()[0]
    assert holding["last_price"] == "46"
    assert holding["price_date"] == "2026-11-13"
    assert holding["market_value"] == "4600.00"
    assert holding["unrealised_pnl"] == "580.00"
    assert holding["unrealised_return"] == "0.144279"
    assert holding["weight"] == "1.000000"


def test_endpoint_includes_closed_positions_when_asked(client_with_data):
    bhp, cba = make_security("BHP"), make_security("CBA", sector="Financials")
    trades = [buy(bhp, "100", "40"), buy(cba, "10", "150"), sell(cba, "10", "160")]

    response = client_with_data(trades).get("/holdings", params={"include_closed": "true"})

    assert [holding["ticker"] for holding in response.json()] == ["BHP", "CBA"]
    assert response.json()[1]["average_cost"] is None
