"""Queries for reading and saving prices."""

from collections.abc import Sequence
from datetime import date

from sqlalchemy import and_, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, joinedload

from app.models import Price, Trade
from app.services.inserts import insert_missing
from app.services.price_provider import DailyClose


def latest_prices(db: Session, up_to: date | None = None) -> dict[str, Price]:
    """Return the most recent price of each security, by ticker, in one query.

    Give up_to to get the most recent price on or before that date instead.
    """
    dates = select(Price.security_id, func.max(Price.price_date).label("price_date"))
    if up_to is not None:
        dates = dates.where(Price.price_date <= up_to)
    latest_dates = dates.group_by(Price.security_id).subquery()
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


def list_prices_of_security(db: Session, security_id: int) -> list[Price]:
    """Return every price of one security, oldest first."""
    statement = select(Price).where(Price.security_id == security_id).order_by(Price.price_date)
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
    rows = [
        {"security_id": security_id, "price_date": close.price_date, "close": close.close}
        for close in closes
    ]
    return len(insert_missing(db, Price, rows, ["security_id", "price_date"], Price.id))
