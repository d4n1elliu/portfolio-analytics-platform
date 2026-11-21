"""Holdings at a past date, with PostgreSQL choosing the trades and prices."""

from datetime import date
from decimal import Decimal

from app.services.holdings import list_holdings
from app.services.prices import latest_prices
from app.services.trades import list_trades_oldest_first
from factories import buy, closes, make_security, sell

MONDAY = date(2026, 11, 9)
TUESDAY = date(2026, 11, 10)
WEDNESDAY = date(2026, 11, 11)
NEXT_SUNDAY = date(2026, 11, 15)


def test_only_the_trades_made_by_the_date_are_listed(db, save):
    bhp = save(make_security("BHP"))
    save(buy(bhp, "1", "40", on=MONDAY), buy(bhp, "2", "40", on=TUESDAY))
    save(buy(bhp, "3", "40", on=WEDNESDAY))

    trades = list_trades_oldest_first(db, up_to=TUESDAY)

    assert [int(trade.quantity) for trade in trades] == [1, 2]


def test_the_price_is_the_latest_one_on_or_before_the_date(db, save):
    bhp, cba = save(make_security("BHP"), make_security("CBA"))
    save(*closes(bhp, {MONDAY: "40", TUESDAY: "41", WEDNESDAY: "42"}))
    save(*closes(cba, {WEDNESDAY: "150"}))

    on_tuesday = latest_prices(db, up_to=TUESDAY)
    on_sunday = latest_prices(db, up_to=NEXT_SUNDAY)

    assert on_tuesday["BHP"].close == Decimal("41")
    assert "CBA" not in on_tuesday
    assert on_sunday["BHP"].price_date == WEDNESDAY


def test_holdings_at_a_past_date_ignore_what_happened_later(db, save):
    bhp, cba = save(make_security("BHP"), make_security("CBA"))
    save(buy(bhp, "100", "40", on=MONDAY), sell(bhp, "100", "45", on=WEDNESDAY))
    save(buy(cba, "10", "150", on=WEDNESDAY))
    save(*closes(bhp, {MONDAY: "40", TUESDAY: "42", WEDNESDAY: "45"}))

    past = list_holdings(db, include_closed=False, as_of=TUESDAY)
    current = list_holdings(db, include_closed=False)

    assert [holding.security.ticker for holding in past] == ["BHP"]
    assert past[0].position.quantity == 100
    assert past[0].valuation.price_date == TUESDAY
    assert past[0].valuation.market_value == 4200
    assert [holding.security.ticker for holding in current] == ["CBA"]


def test_holdings_before_the_first_trade_are_empty(db, save):
    bhp = save(make_security("BHP"))
    save(buy(bhp, "100", "40", on=TUESDAY))

    assert list_holdings(db, include_closed=True, as_of=MONDAY) == []
