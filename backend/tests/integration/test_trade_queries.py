"""The trade queries, run against PostgreSQL."""

from datetime import date

from app.services.trades import list_trades, list_trades_oldest_first
from factories import buy, make_security

MONDAY = date(2026, 11, 9)
TUESDAY = date(2026, 11, 10)


def quantities(trades) -> list[int]:
    return [int(trade.quantity) for trade in trades]


def test_trades_are_paged_newest_first(db, save):
    bhp = save(make_security("BHP"))
    save(buy(bhp, "1", "40", on=MONDAY), buy(bhp, "2", "40", on=TUESDAY))
    # Saved later on the same day, so it is the newest of all.
    save(buy(bhp, "3", "40", on=TUESDAY))

    first_page, total = list_trades(db, limit=2, offset=0)
    second_page, _ = list_trades(db, limit=2, offset=2)

    assert total == 3
    assert quantities(first_page) == [3, 2]
    assert quantities(second_page) == [1]
    assert first_page[0].security.ticker == "BHP"


def test_trades_oldest_first_keeps_the_saved_order_within_a_day(db, save):
    bhp = save(make_security("BHP"))
    save(buy(bhp, "1", "40", on=TUESDAY))
    save(buy(bhp, "2", "40", on=TUESDAY))
    save(buy(bhp, "3", "40", on=MONDAY))

    assert quantities(list_trades_oldest_first(db)) == [3, 1, 2]
