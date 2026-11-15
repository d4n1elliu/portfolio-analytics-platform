"""Endpoints for holdings."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.routes.dependencies import get_current_user
from app.schemas.holding import HoldingRead
from app.services import holdings as holdings_service

router = APIRouter(
    prefix="/holdings", tags=["holdings"], dependencies=[Depends(get_current_user)]
)


@router.get("", response_model=list[HoldingRead])
def list_holdings(
    include_closed: bool = Query(False, description="Also return positions that have been sold."),
    db: Session = Depends(get_db),
):
    """List the current position in each security, ordered by ticker."""
    holdings = holdings_service.list_holdings(db, include_closed=include_closed)
    return [HoldingRead.from_holding(holding) for holding in holdings]
