"""Import a CSV file of trades into the database."""

import hashlib
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.config import IMPORT_MAX_ROWS, MARKET_TIMEZONE
from app.models import ImportBatch, Trade, User
from app.models.import_batch import FILE_NAME_LENGTH
from app.services.csv_parsing import ImportDuplicateError, ImportRowsError, decode_csv, read_rows
from app.services.import_batches import find_by_hash
from app.services.market_time import market_today
from app.services.securities import security_ids_by_ticker
from app.services.trade_csv import REQUIRED_COLUMNS, validate_rows


def import_trades_csv(db: Session, file_name: str, content: bytes, user: User) -> int:
    """Save every row of a trades CSV, or save nothing.

    Returns the number of trades imported. Raises ImportDuplicateError if the
    same file was imported before, ImportFileError if the file cannot be
    read, or ImportRowsError if any row is invalid.
    """
    file_hash = hashlib.sha256(content).hexdigest()
    earlier = find_by_hash(db, file_hash)
    if earlier is not None:
        raise ImportDuplicateError(_already_imported(earlier))

    rows = read_rows(decode_csv(content), REQUIRED_COLUMNS, IMPORT_MAX_ROWS)
    security_ids = security_ids_by_ticker(db)

    trades, errors = validate_rows(rows, set(security_ids), market_today())
    if errors:
        raise ImportRowsError(errors)

    batch = ImportBatch(
        file_name=file_name[:FILE_NAME_LENGTH],
        file_hash=file_hash,
        row_count=len(trades),
        imported_by_id=user.id,
    )
    db.add(batch)
    db.add_all(
        Trade(
            import_batch=batch,
            security_id=security_ids[trade.ticker],
            trade_date=trade.trade_date,
            side=trade.side,
            quantity=trade.quantity,
            price=trade.price,
            fees=trade.fees,
        )
        for trade in trades
    )
    # One transaction: if any insert fails, the database undoes them all.
    db.commit()
    return len(trades)


def _already_imported(earlier: ImportBatch) -> str:
    imported_on = earlier.created_at.astimezone(ZoneInfo(MARKET_TIMEZONE)).date()
    return (
        f"This file was already imported as '{earlier.file_name}' on "
        f"{imported_on.day} {imported_on:%b %Y} "
        f"by {earlier.imported_by.name}. Nothing was saved."
    )
