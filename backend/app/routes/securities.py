"""Endpoints for securities."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.routes.dependencies import get_current_user
from app.schemas.security import SecurityRead
from app.services import securities as securities_service

router = APIRouter(
    prefix="/securities", tags=["securities"], dependencies=[Depends(get_current_user)]
)


@router.get("", response_model=list[SecurityRead])
def list_securities(db: Session = Depends(get_db)):
    """List every security, ordered by ticker."""
    return securities_service.list_securities(db)
