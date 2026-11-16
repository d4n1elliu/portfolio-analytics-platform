"""Unit tests for the portfolio history. No database is used."""

from datetime import date
from decimal import Decimal

from app.schemas.portfolio_history import PortfolioHistoryPoint
from app.services.holdings import build_holdings
from app.services.portfolio_history import build_portfolio_history
from factories import buy, closes, make_security, sell

# One week of trading days, then the weekend and the Monday after it.
LAST_FRI = date(2026, 11, 6)
MON = date(2026, 11, 9)
TUE = date(2026, 11, 10)
WED = date(2026, 11, 11)
THU = date(2026, 11, 12)
FRI = date(2026, 11, 13)
SAT = date(2026, 11, 14)
NEXT_MON = date(2026, 11, 16)


def dates(points) -> list[date]:
    return [point.as_of for point in points]


def market_values(points) -> list[Decimal]:
    return [point.market_value for point in points]


def cost_bases(points) -> list[Decimal]:
    return [point.cost_basis for point in points]


# --- Which dates get a point ---


def test_no_trades_gives_no_points():
    bhp = make_security("BHP")

    assert build_portfolio_history([], closes(bhp, {MON: "41", TUE: "42"})) == []


def test_no_prices_gives_no_points():
    bhp = make_security("BHP")

    assert build_portfolio_history([buy(bhp, "100", "40", on=MON)], []) == []


def test_history_runs_from_the_first_date_held_to_the_latest_price():
    bhp = make_security("BHP")
    trades = [buy(bhp, "100", "40", on=TUE)]
    prices = closes(bhp, {LAST_FRI: "39", MON: "40", TUE: "41", WED: "42", THU: "43"})

    points = build_portfolio_history(trades, prices)

    assert dates(points) == [TUE, WED, THU]


def test_prices_can_be_given_in_any_order():
    bhp = make_security("BHP")
    prices = closes(bhp, {WED: "43", MON: "41", TUE: "42"})

    points = build_portfolio_history([buy(bhp, "100", "40", on=MON)], prices)

    assert dates(points) == [MON, TUE, WED]
    assert market_values(points) == [4100, 4200, 4300]


# --- Buys ---


def test_buys_only_value_moves_with_the_price_and_cost_basis_stays_flat():
    bhp = make_security("BHP")
    trades = [buy(bhp, "100", "40", fees="20", on=MON)]
    prices = closes(bhp, {MON: "41", TUE: "42", WED: "39"})

    points = build_portfolio_history(trades, prices)

    assert market_values(points) == [4100, 4200, 3900]
    assert cost_bases(points) == [4020, 4020, 4020]
    assert [point.unrealised_pnl for point in points] == [80, 180, -120]


def test_second_buy_raises_both_lines_on_its_date():
    bhp = make_security("BHP")
    trades = [buy(bhp, "100", "40", on=MON), buy(bhp, "50", "44", on=WED)]
    prices = closes(bhp, {MON: "41", TUE: "42", WED: "44", THU: "45"})

    points = build_portfolio_history(trades, prices)

    assert market_values(points) == [4100, 4200, 6600, 6750]
    assert cost_bases(points) == [4000, 4000, 6200, 6200]


def test_several_securities_are_added_together():
    bhp, cba = make_security("BHP"), make_security("CBA")
    trades = [buy(bhp, "100", "40", on=MON), buy(cba, "10", "150", on=TUE)]
    prices = closes(bhp, {MON: "41", TUE: "42"}) + closes(cba, {MON: "151", TUE: "152"})

    points = build_portfolio_history(trades, prices)

    # CBA is not held on Monday, so its Monday close is not counted.
    assert market_values(points) == [4100, 4200 + 1520]
    assert cost_bases(points) == [4000, 4000 + 1500]


# --- Sells ---


def test_partial_sell_lowers_both_lines_on_its_date():
    bhp = make_security("BHP")
    trades = [buy(bhp, "100", "40", on=MON), sell(bhp, "40", "45", on=WED)]
    prices = closes(bhp, {MON: "41", TUE: "42", WED: "45"})

    points = build_portfolio_history(trades, prices)

    assert market_values(points) == [4100, 4200, 60 * 45]
    assert cost_bases(points) == [4000, 4000, 2400]


def test_closed_position_contributes_nothing_after_it_closes():
    bhp, cba = make_security("BHP"), make_security("CBA")
    trades = [
        buy(bhp, "100", "40", on=MON),
        buy(cba, "10", "150", on=MON),
        sell(cba, "10", "160", on=WED),
    ]
    days = (MON, TUE, WED, THU)
    prices = closes(bhp, dict.fromkeys(days, "40")) + closes(cba, dict.fromkeys(days, "160"))

    points = build_portfolio_history(trades, prices)

    assert market_values(points) == [5600, 5600, 4000, 4000]
    assert cost_bases(points) == [5500, 5500, 4000, 4000]


def test_points_continue_at_zero_after_everything_is_sold():
    bhp = make_security("BHP")
    trades = [buy(bhp, "100", "40", on=MON), sell(bhp, "100", "45", on=TUE)]
    prices = closes(bhp, {MON: "41", TUE: "45", WED: "46"})

    points = build_portfolio_history(trades, prices)

    assert dates(points) == [MON, TUE, WED]
    assert market_values(points) == [4100, 0, 0]
    assert cost_bases(points) == [4000, 0, 0]


def test_past_dates_use_the_quantity_held_then_not_the_quantity_held_now():
    bhp = make_security("BHP")
    trades = [buy(bhp, "100", "40", on=MON), sell(bhp, "90", "40", on=THU)]
    prices = closes(bhp, dict.fromkeys((MON, TUE, WED, THU), "40"))

    points = build_portfolio_history(trades, prices)

    assert market_values(points) == [4000, 4000, 4000, 400]


# --- Missing prices ---


def test_missing_close_is_carried_forward():
    bhp, cba = make_security("BHP"), make_security("CBA")
    trades = [buy(bhp, "100", "40", on=MON), buy(cba, "10", "150", on=MON)]
    # CBA has no close on Tuesday.
    prices = closes(bhp, {MON: "41", TUE: "42", WED: "43"}) + closes(cba, {MON: "151", WED: "153"})

    points = build_portfolio_history(trades, prices)

    assert dates(points) == [MON, TUE, WED]
    assert market_values(points) == [4100 + 1510, 4200 + 1510, 4300 + 1530]
    assert cost_bases(points) == [5500, 5500, 5500]


def test_close_from_before_the_first_trade_is_carried_forward():
    bhp, cba = make_security("BHP"), make_security("CBA")
    trades = [buy(bhp, "100", "40", on=TUE), buy(cba, "10", "150", on=TUE)]
    prices = closes(bhp, {MON: "41", TUE: "42"}) + closes(cba, {MON: "151"})

    points = build_portfolio_history(trades, prices)

    assert dates(points) == [TUE]
    assert market_values(points) == [4200 + 1510]


def test_held_security_with_no_close_yet_is_left_out_of_both_lines():
    bhp, cba = make_security("BHP"), make_security("CBA")
    trades = [buy(bhp, "100", "40", on=MON), buy(cba, "10", "150", on=MON)]
    # CBA's first close is on Wednesday.
    prices = closes(bhp, {MON: "41", TUE: "42", WED: "43"}) + closes(cba, {WED: "153"})

    points = build_portfolio_history(trades, prices)

    assert market_values(points) == [4100, 4200, 4300 + 1530]
    assert cost_bases(points) == [4000, 4000, 4000 + 1500]
    assert [point.unrealised_pnl for point in points] == [100, 200, 330]


# --- Trades on days without prices ---


def test_weekend_trade_takes_effect_on_the_next_priced_date():
    bhp = make_security("BHP")
    trades = [buy(bhp, "100", "40", on=MON), buy(bhp, "50", "44", on=SAT)]
    prices = closes(bhp, {FRI: "44", NEXT_MON: "46"})

    points = build_portfolio_history(trades, prices)

    assert dates(points) == [FRI, NEXT_MON]
    assert market_values(points) == [4400, 150 * 46]
    assert cost_bases(points) == [4000, 6200]


def test_history_starts_on_the_next_priced_date_when_the_first_trade_is_on_a_weekend():
    bhp = make_security("BHP")
    prices = closes(bhp, {FRI: "44", NEXT_MON: "46"})

    points = build_portfolio_history([buy(bhp, "100", "45", on=SAT)], prices)

    assert dates(points) == [NEXT_MON]
    assert market_values(points) == [4600]


# --- Precision ---


def test_points_are_not_rounded():
    bhp = make_security("BHP")
    trades = [buy(bhp, "3", "10", fees="1", on=MON), sell(bhp, "1", "10", on=TUE)]
    prices = closes(bhp, {MON: "10.123456", TUE: "10.123456"})

    point = build_portfolio_history(trades, prices)[-1]

    # Two thirds of 31 is left, which is not a whole number of cents.
    assert point.cost_basis == Decimal("31") - Decimal("31") / 3
    assert point.market_value == Decimal("20.246912")
    assert point.unrealised_pnl == point.market_value - point.cost_basis


def test_response_rounds_money_to_cents():
    bhp = make_security("BHP")
    trades = [buy(bhp, "3", "10", fees="1", on=MON), sell(bhp, "1", "10", on=TUE)]
    prices = closes(bhp, {MON: "10.123456", TUE: "10.123456"})

    point = PortfolioHistoryPoint.from_point(build_portfolio_history(trades, prices)[-1])

    assert point.date == TUE
    assert str(point.market_value) == "20.25"
    assert str(point.cost_basis) == "20.67"
    assert str(point.unrealised_pnl) == "-0.42"


# --- Consistency with holdings ---


def test_last_point_equals_the_holdings_totals():
    bhp, cba, wes, xro = (make_security(ticker) for ticker in ("BHP", "CBA", "WES", "XRO"))
    trades = [
        buy(bhp, "400", "41.85", fees="29.95", on=MON),
        buy(cba, "110", "155.353788", on=MON),
        buy(wes, "75", "71.20", fees="19.95", on=TUE),
        buy(bhp, "200", "43.10", fees="19.95", on=WED),
        sell(wes, "75", "73.05", fees="19.95", on=WED),
        sell(bhp, "250", "45.72", fees="29.95", on=THU),
        # Held, but never priced.
        buy(xro, "20", "170", on=THU),
    ]
    bhp_closes = closes(bhp, {MON: "42", TUE: "42.5", WED: "43", THU: "45.5", FRI: "46.10"})
    # CBA's latest close is Thursday's, so it is carried forward to Friday.
    cba_closes = closes(cba, {MON: "156", TUE: "157", THU: "158"})
    wes_closes = closes(wes, {MON: "71", TUE: "72", WED: "73", THU: "74", FRI: "75"})
    latest = {"BHP": bhp_closes[-1], "CBA": cba_closes[-1], "WES": wes_closes[-1]}

    last_point = build_portfolio_history(trades, bhp_closes + cba_closes + wes_closes)[-1]
    valued = [
        holding
        for holding in build_holdings(trades, include_closed=False, prices=latest)
        if holding.valuation is not None
    ]

    assert last_point.as_of == FRI
    assert [holding.security.ticker for holding in valued] == ["BHP", "CBA"]
    assert last_point.market_value == sum(holding.valuation.market_value for holding in valued)
    assert last_point.cost_basis == sum(holding.position.cost_basis for holding in valued)
    assert last_point.unrealised_pnl == sum(holding.valuation.unrealised_pnl for holding in valued)


# --- Cash put in and taken out ---


def net_flows(points) -> list[Decimal]:
    return [point.net_flow for point in points]


def test_buy_puts_in_its_cost_and_fees():
    bhp = make_security("BHP")
    trades = [buy(bhp, "100", "40", fees="20", on=MON)]

    points = build_portfolio_history(trades, closes(bhp, {MON: "41", TUE: "42"}))

    assert net_flows(points) == [Decimal("4020"), Decimal("0")]


def test_sell_takes_out_its_proceeds_after_fees():
    bhp = make_security("BHP")
    trades = [buy(bhp, "100", "40", on=MON), sell(bhp, "40", "45", fees="10", on=TUE)]

    points = build_portfolio_history(trades, closes(bhp, {MON: "40", TUE: "45"}))

    assert net_flows(points) == [Decimal("4000"), Decimal("-1790")]


def test_trades_on_one_date_are_added_together():
    bhp, cba = make_security("BHP"), make_security("CBA")
    trades = [buy(bhp, "100", "40", on=MON), buy(cba, "10", "150", on=MON)]
    prices = closes(bhp, {MON: "40"}) + closes(cba, {MON: "150"})

    assert net_flows(build_portfolio_history(trades, prices)) == [Decimal("5500")]


def test_weekend_trade_counts_as_cash_on_the_next_priced_date():
    bhp = make_security("BHP")
    trades = [buy(bhp, "100", "40", on=FRI), buy(bhp, "50", "42", on=SAT)]

    points = build_portfolio_history(trades, closes(bhp, {FRI: "40", NEXT_MON: "42"}))

    assert net_flows(points) == [Decimal("4000"), Decimal("2100")]


def test_position_with_no_close_puts_in_no_cash_until_it_is_priced():
    bhp, cba = make_security("BHP"), make_security("CBA")
    trades = [buy(bhp, "100", "40", on=MON), buy(cba, "10", "150", on=MON)]
    prices = closes(bhp, {MON: "40", TUE: "40", WED: "40"}) + closes(cba, {WED: "160"})

    points = build_portfolio_history(trades, prices)

    # CBA arrives on Wednesday at what it is then worth, not at what it cost.
    assert net_flows(points) == [Decimal("4000"), Decimal("0"), Decimal("1600")]
    assert market_values(points) == [Decimal("4000"), Decimal("4000"), Decimal("5600")]


# --- Endpoint ---


def test_endpoint_returns_one_point_per_date_oldest_first(client_with_data):
    bhp = make_security("BHP")
    trades = [buy(bhp, "100", "40", fees="20", on=MON), sell(bhp, "40", "45", on=WED)]
    prices = closes(bhp, {MON: "41.005", TUE: "39", WED: "45"})

    response = client_with_data(trades, prices).get("/portfolio/history")

    assert response.status_code == 200
    assert response.json() == [
        {
            "date": "2026-11-09",
            "market_value": "4100.50",
            "cost_basis": "4020.00",
            "unrealised_pnl": "80.50",
        },
        {
            "date": "2026-11-10",
            "market_value": "3900.00",
            "cost_basis": "4020.00",
            "unrealised_pnl": "-120.00",
        },
        {
            "date": "2026-11-11",
            "market_value": "2700.00",
            "cost_basis": "2412.00",
            "unrealised_pnl": "288.00",
        },
    ]


def test_endpoint_returns_an_empty_list_without_trades(client_with_data):
    bhp = make_security("BHP")

    response = client_with_data([], closes(bhp, {MON: "41"})).get("/portfolio/history")

    assert response.status_code == 200
    assert response.json() == []
