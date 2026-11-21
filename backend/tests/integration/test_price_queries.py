"""The price queries, run against PostgreSQL."""

from datetime import date
from decimal import Decimal

from sqlalchemy import select

from app.models import Price
from app.services.price_provider import DailyClose
from app.services.prices import (
    insert_new_closes,
    latest_price_dates,
    latest_prices,
    list_prices_of_traded_securities,
    save_closes,
)
from factories import buy, closes, make_security

MONDAY = date(2026, 11, 9)
TUESDAY = date(2026, 11, 10)


def stored_closes(db, security) -> dict[date, Decimal]:
    statement = select(Price.price_date, Price.close).where(Price.security_id == security.id)
    return dict(db.execute(statement).all())


def test_latest_prices_returns_the_newest_price_of_each_security(db, save):
    bhp, cba = save(make_security("BHP"), make_security("CBA"))
    save(*closes(bhp, {MONDAY: "40", TUESDAY: "41"}), *closes(cba, {MONDAY: "150"}))

    latest = latest_prices(db)

    assert {ticker: (price.price_date, price.close) for ticker, price in latest.items()} == {
        "BHP": (TUESDAY, Decimal("41")),
        "CBA": (MONDAY, Decimal("150")),
    }


def test_latest_price_dates_are_by_security_id(db, save):
    bhp, cba = save(make_security("BHP"), make_security("CBA"))
    save(*closes(bhp, {MONDAY: "40", TUESDAY: "41"}))

    assert latest_price_dates(db) == {bhp.id: TUESDAY}
    assert cba.id not in latest_price_dates(db)


def test_only_the_prices_of_traded_securities_are_listed(db, save):
    bhp, cba = save(make_security("BHP"), make_security("CBA"))
    save(buy(bhp, "10", "40"), *closes(bhp, {MONDAY: "40"}), *closes(cba, {MONDAY: "150"}))

    prices = list_prices_of_traded_securities(db)

    assert [price.security.ticker for price in prices] == ["BHP"]


def test_save_closes_replaces_the_price_already_stored_for_a_day(db, save):
    bhp = save(make_security("BHP"))
    save(*closes(bhp, {MONDAY: "40"}))

    saved = save_closes(
        db, bhp.id, [DailyClose(MONDAY, Decimal("40.5")), DailyClose(TUESDAY, Decimal("41"))]
    )

    assert saved == 2
    assert stored_closes(db, bhp) == {MONDAY: Decimal("40.5"), TUESDAY: Decimal("41")}


def test_insert_new_closes_leaves_the_price_already_stored_for_a_day(db, save):
    bhp = save(make_security("BHP"))
    save(*closes(bhp, {MONDAY: "40"}))

    added = insert_new_closes(
        db, bhp.id, [DailyClose(MONDAY, Decimal("40.5")), DailyClose(TUESDAY, Decimal("41"))]
    )

    assert added == 1
    assert stored_closes(db, bhp) == {MONDAY: Decimal("40"), TUESDAY: Decimal("41")}
