"""Endpoints for trades."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Role
from app.routes.dependencies import (
    PageParams,
    page_params,
    read_csv_upload,
    require_role,
)
from app.routes.errors import IMPORT_ERROR_RESPONSES
from app.schemas.common import ImportResult, Page
from app.schemas.trade import TradeRead
from app.services import trades as trades_service
from app.services.trade_import import import_trades_csv

router = APIRouter(prefix="/trades", tags=["trades"])


@router.get("", response_model=Page[TradeRead])
def list_trades(page: PageParams = Depends(page_params), db: Session = Depends(get_db)):
    """List trades, newest first."""
    trades, total = trades_service.list_trades(db, limit=page.limit, offset=page.offset)
    return Page(
        items=[TradeRead.from_trade(trade) for trade in trades],
        total=total,
        limit=page.limit,
        offset=page.offset,
    )


@router.post(
    "/import",
    response_model=ImportResult,
    status_code=status.HTTP_201_CREATED,
    responses=IMPORT_ERROR_RESPONSES,
    dependencies=[Depends(require_role(Role.OPERATIONS))],
)
def import_trades(content: bytes = Depends(read_csv_upload), db: Session = Depends(get_db)):
    """Import trades from a CSV file. Either every row is saved or none are.

    Only the Operations role may import.
    """
    return ImportResult(imported=import_trades_csv(db, content))
