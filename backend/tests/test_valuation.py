"""Unit tests for valuing a position. No database is used."""

from datetime import date
from decimal import Decimal

from app.services.positions import Position
from app.services.valuation import portfolio_weights, value_position

CENTS = Decimal("0.01")
FOUR_PLACES = Decimal("0.0001")
PRICE_DATE = date(2026, 11, 13)


def position(quantity: str, cost_basis: str) -> Position:
    return Position(
        quantity=Decimal(quantity),
        cost_basis=Decimal(cost_basis),
        realised_pnl=Decimal("0"),
        oversold_quantity=Decimal("0"),
    )


def value(quantity: str, cost_basis: str, close: str):
    return value_position(position(quantity, cost_basis), Decimal(close), PRICE_DATE)


# --- Valuing a position ---


def test_price_above_cost_gives_an_unrealised_profit():
    valuation = value("100", "1000", "12")

    assert valuation.market_value == 1200
    assert valuation.unrealised_pnl == 200
    assert valuation.unrealised_return == Decimal("0.2")


def test_price_below_cost_gives_an_unrealised_loss():
    valuation = value("100", "1000", "7")

    assert valuation.market_value == 700
    assert valuation.unrealised_pnl == -300
    assert valuation.unrealised_return == Decimal("-0.3")


def test_price_equal_to_average_cost_gives_zero_not_none():
    valuation = value("100", "1000", "10")

    assert valuation.unrealised_pnl == 0
    assert valuation.unrealised_return == 0


def test_price_and_date_are_carried_through():
    valuation = value("100", "1000", "12.345678")

    assert valuation.last_price == Decimal("12.345678")
    assert valuation.price_date == PRICE_DATE


def test_position_that_cost_nothing_has_no_return():
    valuation = value("0", "0", "12")

    assert valuation.market_value == 0
    assert valuation.unrealised_pnl == 0
    assert valuation.unrealised_return is None


def test_sample_bhp_position_at_a_made_up_price():
    valuation = value("350", "14822.441667", "46.10")

    assert valuation.market_value == Decimal("16135.00")
    assert valuation.unrealised_pnl.quantize(CENTS) == Decimal("1312.56")
    assert valuation.unrealised_return.quantize(FOUR_PLACES) == Decimal("0.0886")


# --- Portfolio weights ---


def test_weights_are_each_holding_over_the_total():
    weights = portfolio_weights({"BHP": Decimal("3000"), "CBA": Decimal("1000")})

    assert weights == {"BHP": Decimal("0.75"), "CBA": Decimal("0.25")}


def test_weights_add_up_to_one():
    # Thirds do not divide evenly, so the total is compared after rounding.
    weights = portfolio_weights({"A": Decimal("1"), "B": Decimal("1"), "C": Decimal("1")})

    assert sum(weights.values()).quantize(FOUR_PLACES) == 1


def test_single_holding_has_a_weight_of_one():
    assert portfolio_weights({"BHP": Decimal("16135")}) == {"BHP": Decimal("1")}


def test_no_holdings_gives_no_weights():
    assert portfolio_weights({}) == {}


def test_total_of_zero_gives_no_weights():
    assert portfolio_weights({"BHP": Decimal("0"), "CBA": Decimal("0")}) == {}
