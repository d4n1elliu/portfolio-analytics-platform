"""Queries for reading trades."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Trade


def list_trades_oldest_first(db: Session) -> list[Trade]:
    """Return every trade, with its security, oldest first."""
    statement = (
        select(Trade)
        .options(joinedload(Trade.security))
        # The id decides the order of trades on the same day.
        .order_by(Trade.trade_date, Trade.id)
    )
    return list(db.scalars(statement))


def list_trades(db: Session, limit: int, offset: int) -> tuple[list[Trade], int]:
    """Return one page of trades, newest first, and the total number of trades."""
    total = db.scalar(select(func.count()).select_from(Trade)) or 0
    statement = (
        select(Trade)
        # Load each trade's security in the same query.
        .options(joinedload(Trade.security))
        # The id breaks ties so the order is the same on every page.
        .order_by(Trade.trade_date.desc(), Trade.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(statement)), total
