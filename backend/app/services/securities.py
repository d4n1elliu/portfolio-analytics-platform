"""Queries for reading securities."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Security


def list_securities(db: Session) -> list[Security]:
    """Return every security, ordered by ticker."""
    return list(db.scalars(select(Security).order_by(Security.ticker)))


def security_ids_by_ticker(db: Session) -> dict[str, int]:
    """Return every ticker with its security id, using a single query."""
    return dict(db.execute(select(Security.ticker, Security.id)).all())
