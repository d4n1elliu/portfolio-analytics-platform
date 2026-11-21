"""Endpoints for trades."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TradeSide, User
from app.routes.dependencies import (
    PageParams,
    SortOrder,
    UploadedFile,
    get_current_user,
    page_of,
    page_params,
    read_csv_upload,
    require_permission,
)
from app.routes.errors import IMPORT_ERROR_RESPONSES
from app.schemas.common import ImportResult, Page
from app.schemas.import_batch import ImportBatchRead
from app.schemas.trade import TradeRead
from app.services import import_batches as import_batches_service
from app.services import trades as trades_service
from app.services.permissions import Permission
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


@router.get(
    "/export",
    response_class=Response,
    responses={200: {"content": {"text/csv": {}}}},
    dependencies=[Depends(require_permission(Permission.EXPORT_TRADES))],
)
def export_trades(query: TradeQuery = Depends(trade_query), db: Session = Depends(get_db)):
    """Download every trade that matches the filters as a CSV file.

    Needs the permission to export trades.
    """
    return Response(
        trades_to_csv(trades_service.list_all_trades(db, query)),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{EXPORT_FILE_NAME}"'},
    )


@router.get("/imports", response_model=Page[ImportBatchRead])
def list_imports(page: PageParams = Depends(page_params), db: Session = Depends(get_db)):
    """List the files that have been imported, newest first."""
    batches, total = import_batches_service.list_import_batches(
        db, limit=page.limit, offset=page.offset
    )
    return page_of([ImportBatchRead.from_batch(batch) for batch in batches], total, page)


@router.post(
    "/import",
    response_model=ImportResult,
    status_code=status.HTTP_201_CREATED,
    responses=IMPORT_ERROR_RESPONSES,
    dependencies=[Depends(require_permission(Permission.IMPORT_TRADES))],
)
def import_trades(
    upload: UploadedFile = Depends(read_csv_upload),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Import trades from a CSV file. Either every row is saved or none are.

    Needs the permission to import trades. A file that was imported before is refused.
    """
    return ImportResult(imported=import_trades_csv(db, upload.file_name, upload.content, user))
