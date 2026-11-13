"""Unit tests for the position calculation. No database is used."""

from decimal import Decimal

from app.models import Trade, TradeSide
from app.services.positions import calculate_position

CENTS = Decimal("0.01")
SIX_PLACES = Decimal("0.000001")


def buy(quantity: str, price: str, fees: str = "0") -> Trade:
    return _trade(TradeSide.BUY, quantity, price, fees)


def sell(quantity: str, price: str, fees: str = "0") -> Trade:
    return _trade(TradeSide.SELL, quantity, price, fees)


def _trade(side: TradeSide, quantity: str, price: str, fees: str) -> Trade:
    return Trade(side=side, quantity=Decimal(quantity), price=Decimal(price), fees=Decimal(fees))


# --- Buys only ---


def test_no_trades_gives_an_empty_position():
    position = calculate_position([])

    assert position.quantity == 0
    assert position.cost_basis == 0
    assert position.realised_pnl == 0
    assert position.oversold_quantity == 0
    assert position.average_cost is None
    assert not position.is_open


def test_one_buy_is_held_at_its_price():
    position = calculate_position([buy("100", "10")])

    assert position.quantity == 100
    assert position.cost_basis == 1000
    assert position.average_cost == 10
    assert position.realised_pnl == 0
    assert position.is_open


def test_several_buys_at_different_prices_give_a_weighted_average():
    position = calculate_position([buy("100", "10"), buy("300", "20")])

    assert position.quantity == 400
    assert position.cost_basis == 7000
    assert position.average_cost == Decimal("17.5")


def test_buy_fees_are_added_to_the_cost_basis():
    position = calculate_position([buy("100", "10", fees="20")])

    assert position.cost_basis == 1020
    assert position.average_cost == Decimal("10.2")


# --- Sells ---


def test_partial_sell_keeps_the_average_and_realises_a_profit():
    position = calculate_position([buy("100", "10"), sell("40", "15")])

    assert position.quantity == 60
    assert position.average_cost == 10
    assert position.cost_basis == 600
    assert position.realised_pnl == 200


def test_selling_below_cost_realises_a_loss():
    position = calculate_position([buy("100", "10"), sell("40", "7")])

    assert position.realised_pnl == -120


def test_sell_fees_reduce_the_realised_profit():
    position = calculate_position([buy("100", "10"), sell("40", "15", fees="25")])

    assert position.realised_pnl == 175
    assert position.cost_basis == 600


def test_full_sell_closes_the_position_and_keeps_the_profit():
    # The average, 10 / 3, does not divide evenly.
    position = calculate_position([buy("3", "3", fees="1"), sell("3", "5")])

    assert position.quantity == 0
    assert position.cost_basis == 0
    assert position.average_cost is None
    assert position.realised_pnl == 5
    assert not position.is_open


def test_buy_after_a_full_sell_starts_a_new_average():
    position = calculate_position([buy("100", "10"), sell("100", "12"), buy("50", "20")])

    assert position.quantity == 50
    assert position.average_cost == 20
    assert position.realised_pnl == 200


def test_buy_after_a_partial_sell_changes_the_average_but_not_the_profit():
    position = calculate_position([buy("100", "10"), sell("50", "12"), buy("50", "20")])

    assert position.quantity == 100
    assert position.average_cost == 15
    assert position.realised_pnl == 100


# --- Sells exceeding buys ---


def test_sell_larger_than_the_position_sells_only_what_is_held():
    position = calculate_position([buy("100", "10"), sell("150", "12")])

    assert position.quantity == 0
    assert position.cost_basis == 0
    assert position.oversold_quantity == 50
    # Profit is counted on the 100 units held.
    assert position.realised_pnl == 200


def test_oversold_sell_counts_only_its_share_of_the_fees():
    position = calculate_position([buy("100", "10"), sell("200", "12", fees="30")])

    # Half of the sell was held, so half of the fee is counted.
    assert position.realised_pnl == 185
    assert position.oversold_quantity == 100


def test_sell_with_nothing_held_is_all_oversold():
    position = calculate_position([sell("40", "15", fees="20")])

    assert position.quantity == 0
    assert position.realised_pnl == 0
    assert position.oversold_quantity == 40


def test_buy_after_an_oversold_sell_is_held_in_full():
    position = calculate_position([sell("40", "15"), buy("100", "10")])

    assert position.quantity == 100
    assert position.average_cost == 10
    assert position.oversold_quantity == 40


# --- Figures from sample_data/trades_sample.csv ---


def test_sample_bhp_trades():
    position = calculate_position(
        [
            buy("400", "41.85", fees="29.95"),
            buy("200", "43.10", fees="19.95"),
            sell("250", "45.72", fees="29.95"),
        ]
    )

    assert position.quantity == 350
    assert position.average_cost.quantize(SIX_PLACES) == Decimal("42.349833")
    assert position.cost_basis.quantize(CENTS) == Decimal("14822.44")
    assert position.realised_pnl.quantize(CENTS) == Decimal("812.59")
    assert position.oversold_quantity == 0


def test_sample_cba_trades():
    position = calculate_position(
        [
            buy("120", "152.40", fees="29.95"),
            sell("40", "158.25", fees="29.95"),
            buy("30", "161.90", fees="19.95"),
        ]
    )

    assert position.quantity == 110
    assert position.average_cost.quantize(SIX_PLACES) == Decimal("155.353788")
    assert position.cost_basis.quantize(CENTS) == Decimal("17088.92")
    assert position.realised_pnl.quantize(CENTS) == Decimal("194.07")
