"""Endpoints for the portfolio as a whole."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.portfolio_history import PortfolioHistoryPoint
from app.schemas.portfolio_performance import PerformanceRead
from app.services import portfolio_history as portfolio_history_service
from app.services import portfolio_performance as portfolio_performance_service

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/history", response_model=list[PortfolioHistoryPoint])
def list_portfolio_history(db: Session = Depends(get_db)):
    """List the market value and cost basis of the portfolio on each priced date, oldest first."""
    points = portfolio_history_service.list_portfolio_history(db)
    return [PortfolioHistoryPoint.from_point(point) for point in points]


@router.get("/performance", response_model=PerformanceRead)
def read_portfolio_performance(db: Session = Depends(get_db)):
    """Return the time-weighted return of the portfolio over each period."""
    return PerformanceRead.from_performance(portfolio_performance_service.list_performance(db))
