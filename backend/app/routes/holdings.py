"""Endpoints for holdings."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.holding import HoldingRead
from app.services import holdings as holdings_service
from app.services.market_time import market_today

router = APIRouter(prefix="/holdings", tags=["holdings"])


@router.get("", response_model=list[HoldingRead])
def list_holdings(
    include_closed: bool = Query(False, description="Also return positions that have been sold."),
    as_of: date | None = Query(None, description="Return the positions at the end of this date."),
    db: Session = Depends(get_db),
):
    """List the position in each security, ordered by ticker. Current unless a date is given."""
    if as_of is not None and as_of > market_today():
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "The date must not be in the future."
        )
    holdings = holdings_service.list_holdings(db, include_closed=include_closed, as_of=as_of)
    return [HoldingRead.from_holding(holding) for holding in holdings]
