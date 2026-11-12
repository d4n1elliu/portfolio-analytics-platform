"""Queries for reading trades."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Trade


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
