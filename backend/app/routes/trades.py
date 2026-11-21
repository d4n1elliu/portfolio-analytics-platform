"""Endpoints for trades."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Role, TradeSide
from app.routes.dependencies import (
    PageParams,
    SortOrder,
    page_of,
    page_params,
    read_csv_upload,
    require_role,
)
from app.routes.errors import IMPORT_ERROR_RESPONSES
from app.schemas.common import ImportResult, Page
from app.schemas.trade import TradeRead
from app.services import trades as trades_service
from app.services.trade_export import trades_to_csv
from app.services.trade_import import import_trades_csv
from app.services.trades import TradeQuery, TradeSort

router = APIRouter(prefix="/trades", tags=["trades"])

EXPORT_FILE_NAME = "trades.csv"


def trade_query(
    ticker: str | None = Query(None, max_length=12, description="Only this ticker."),
    side: TradeSide | None = Query(None, description="Only buys or only sells."),
    date_from: date | None = Query(None, description="Only trades on or after this date."),
    date_to: date | None = Query(None, description="Only trades on or before this date."),
    sort: TradeSort = Query(TradeSort.TRADE_DATE, description="The column to order by."),
    order: SortOrder = Query(SortOrder.DESC, description="Ascending or descending."),
) -> TradeQuery:
    """Read the filters and the order from the query string. Use with Depends()."""
    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "The start date must not be after the end date."
        )
    return TradeQuery(
        ticker=(ticker or "").strip().upper() or None,
        side=side,
        date_from=date_from,
        date_to=date_to,
        sort=sort,
        descending=order == SortOrder.DESC,
    )


@router.get("", response_model=Page[TradeRead])
def list_trades(
    query: TradeQuery = Depends(trade_query),
    page: PageParams = Depends(page_params),
    db: Session = Depends(get_db),
):
    """List the trades that match the filters. Newest first unless another order is asked for."""
    trades, total = trades_service.list_trades(db, query, limit=page.limit, offset=page.offset)
    return page_of([TradeRead.from_trade(trade) for trade in trades], total, page)


@router.get("/export", response_class=Response, responses={200: {"content": {"text/csv": {}}}})
def export_trades(query: TradeQuery = Depends(trade_query), db: Session = Depends(get_db)):
    """Download every trade that matches the filters as a CSV file."""
    return Response(
        trades_to_csv(trades_service.list_all_trades(db, query)),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{EXPORT_FILE_NAME}"'},
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
