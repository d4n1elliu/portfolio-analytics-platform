"""Endpoints for the portfolio as a whole."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.routes.dependencies import get_current_user
from app.schemas.portfolio_history import PortfolioHistoryPoint
from app.services import portfolio_history as portfolio_history_service

router = APIRouter(
    prefix="/portfolio", tags=["portfolio"], dependencies=[Depends(get_current_user)]
)


@router.get("/history", response_model=list[PortfolioHistoryPoint])
def list_portfolio_history(db: Session = Depends(get_db)):
    """List the market value and cost basis of the portfolio on each priced date, oldest first."""
    points = portfolio_history_service.list_portfolio_history(db)
    return [PortfolioHistoryPoint.from_point(point) for point in points]
