"""Endpoints for securities."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Security
from app.routes.dependencies import get_security
from app.schemas.security import PriceRead, SecurityRead
from app.services import prices as prices_service
from app.services import securities as securities_service

router = APIRouter(prefix="/securities", tags=["securities"])


@router.get("", response_model=list[SecurityRead])
def list_securities(db: Session = Depends(get_db)):
    """List every security, ordered by ticker."""
    return securities_service.list_securities(db)


@router.get("/{ticker}/prices", response_model=list[PriceRead])
def list_security_prices(security: Security = Depends(get_security), db: Session = Depends(get_db)):
    """List the closing prices of one security, oldest first."""
    prices = prices_service.list_prices_of_security(db, security.id)
    return [PriceRead.from_price(price) for price in prices]
