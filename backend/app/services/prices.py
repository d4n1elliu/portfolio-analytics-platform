"""Queries for reading and saving prices."""

from collections.abc import Sequence
from datetime import date

from sqlalchemy import and_, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, joinedload

from app.models import Price, Trade
from app.services.price_provider import DailyClose


def latest_prices(db: Session) -> dict[str, Price]:
    """Return the most recent price of each security, by ticker, in one query."""
    latest_dates = (
        select(Price.security_id, func.max(Price.price_date).label("price_date"))
        .group_by(Price.security_id)
        .subquery()
    )
    statement = (
        select(Price)
        .join(
            latest_dates,
            and_(
                Price.security_id == latest_dates.c.security_id,
                Price.price_date == latest_dates.c.price_date,
            ),
        )
        .options(joinedload(Price.security))
    )
    return {price.security.ticker: price for price in db.scalars(statement)}


def list_prices_of_traded_securities(db: Session) -> list[Price]:
    """Return every price, with its security, of the securities that have trades."""
    statement = (
        select(Price)
        .options(joinedload(Price.security))
        .where(Price.security_id.in_(select(Trade.security_id)))
    )
    return list(db.scalars(statement))


def latest_price_dates(db: Session) -> dict[int, date]:
    """Return the date of each security's most recent price, by security id."""
    statement = select(Price.security_id, func.max(Price.price_date)).group_by(Price.security_id)
    return dict(db.execute(statement).all())


def save_closes(db: Session, security_id: int, closes: Sequence[DailyClose]) -> int:
    """Save the closes, replacing any price already stored for the same day.

    Returns how many were saved. The caller commits.
    """
    if not closes:
        return 0
    statement = insert(Price).values(
        [
            {"security_id": security_id, "price_date": close.price_date, "close": close.close}
            for close in closes
        ]
    )
    statement = statement.on_conflict_do_update(
        index_elements=["security_id", "price_date"],
        set_={"close": statement.excluded.close},
    )
    db.execute(statement)
    return len(closes)


def insert_new_closes(db: Session, security_id: int, closes: Sequence[DailyClose]) -> int:
    """Save the closes, leaving alone any day that already has a price.

    Returns how many were added. The caller commits.
    """
    if not closes:
        return 0
    statement = (
        insert(Price)
        .values(
            [
                {"security_id": security_id, "price_date": close.price_date, "close": close.close}
                for close in closes
            ]
        )
        .on_conflict_do_nothing(index_elements=["security_id", "price_date"])
        .returning(Price.id)
    )
    return len(db.execute(statement).scalars().all())
