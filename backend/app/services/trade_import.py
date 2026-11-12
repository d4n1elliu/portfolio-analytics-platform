"""Import a CSV file of trades into the database."""

from sqlalchemy.orm import Session

from app.config import IMPORT_MAX_ROWS
from app.models import Trade
from app.services.csv_parsing import ImportRowsError, decode_csv, read_rows
from app.services.market_time import market_today
from app.services.securities import security_ids_by_ticker
from app.services.trade_csv import REQUIRED_COLUMNS, validate_rows


def import_trades_csv(db: Session, content: bytes) -> int:
    """Save every row of a trades CSV, or save nothing.

    Returns the number of trades imported. Raises ImportFileError if the file
    cannot be read, or ImportRowsError if any row is invalid.
    """
    rows = read_rows(decode_csv(content), REQUIRED_COLUMNS, IMPORT_MAX_ROWS)
    security_ids = security_ids_by_ticker(db)

    trades, errors = validate_rows(rows, set(security_ids), market_today())
    if errors:
        raise ImportRowsError(errors)

    db.add_all(
        Trade(
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
