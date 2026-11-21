"""The trade queries, run against PostgreSQL."""

from datetime import date

from app.models import TradeSide
from app.services.trades import (
    TradeQuery,
    TradeSort,
    list_all_trades,
    list_trades,
    list_trades_oldest_first,
)
from factories import buy, make_security, sell

MONDAY = date(2026, 11, 9)
TUESDAY = date(2026, 11, 10)
WEDNESDAY = date(2026, 11, 11)


def quantities(trades) -> list[int]:
    return [int(trade.quantity) for trade in trades]


def test_trades_are_paged_newest_first(db, save):
    bhp = save(make_security("BHP"))
    save(buy(bhp, "1", "40", on=MONDAY), buy(bhp, "2", "40", on=TUESDAY))
    save(buy(bhp, "3", "40", on=TUESDAY))

    first_page, total = list_trades(db, TradeQuery(), limit=2, offset=0)
    second_page, _ = list_trades(db, TradeQuery(), limit=2, offset=2)

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


def test_filters_narrow_the_trades_and_the_total(db, save):
    bhp, cba = save(make_security("BHP"), make_security("CBA"))
    save(
        buy(bhp, "1", "40", on=MONDAY),
        sell(bhp, "2", "41", on=TUESDAY),
        buy(cba, "3", "150", on=TUESDAY),
        buy(bhp, "4", "42", on=WEDNESDAY),
    )

    def matching(query: TradeQuery) -> list[int]:
        trades, total = list_trades(db, query, limit=10, offset=0)
        assert total == len(trades)
        return sorted(quantities(trades))

    assert matching(TradeQuery(ticker="BHP")) == [1, 2, 4]
    assert matching(TradeQuery(side=TradeSide.SELL)) == [2]
    assert matching(TradeQuery(date_from=TUESDAY)) == [2, 3, 4]
    assert matching(TradeQuery(date_to=TUESDAY)) == [1, 2, 3]
    assert matching(TradeQuery(ticker="BHP", date_from=TUESDAY, date_to=TUESDAY)) == [2]
    assert matching(TradeQuery(ticker="XYZ")) == []


def test_the_total_counts_every_match_not_just_the_page(db, save):
    bhp, cba = save(make_security("BHP"), make_security("CBA"))
    save(buy(bhp, "1", "40"), buy(bhp, "2", "40"), buy(cba, "3", "150"))

    page, total = list_trades(db, TradeQuery(ticker="BHP"), limit=1, offset=0)

    assert total == 2
    assert len(page) == 1


def test_trades_can_be_ordered_by_another_column(db, save):
    bhp, cba = save(make_security("BHP"), make_security("CBA"))
    save(buy(cba, "3", "150"), buy(bhp, "1", "40"), buy(cba, "2", "151"))

    by_quantity = TradeQuery(sort=TradeSort.QUANTITY, descending=False)
    by_ticker = TradeQuery(sort=TradeSort.TICKER, descending=False)

    assert quantities(list_all_trades(db, by_quantity)) == [1, 2, 3]
    assert quantities(list_all_trades(db, by_ticker)) == [1, 3, 2]
