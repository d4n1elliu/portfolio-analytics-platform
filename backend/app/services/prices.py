"""Queries for reading prices."""

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Price


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
