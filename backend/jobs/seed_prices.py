"""Load the committed price history into the database.

Run from the backend/ directory with:
    python -m jobs.seed_prices

Safe to run more than once: a day that already has a price is left alone.
Needs no network.
"""

import sys
from datetime import date

from sqlalchemy.orm import Session

from app.config import BACKEND_DIR
from app.database import SessionLocal
from app.services.csv_parsing import ImportRowsError, decode_csv, read_rows
from app.services.market_time import market_today
from app.services.price_csv import REQUIRED_COLUMNS, closes_by_ticker, validate_rows
from app.services.prices import insert_new_closes
from app.services.securities import security_ids_by_ticker

PRICE_HISTORY_FILE = BACKEND_DIR / "sample_data" / "prices_history.csv"
MAX_ROWS = 10_000


def seed_prices(db: Session, content: bytes, today: date) -> int:
    """Add every price in the CSV that is not stored yet. Returns how many were added.

    Raises ImportRowsError if any row is invalid, and adds nothing.
    """
    rows = read_rows(decode_csv(content), REQUIRED_COLUMNS, MAX_ROWS)
    security_ids = security_ids_by_ticker(db)

    prices, errors = validate_rows(rows, set(security_ids), today)
    if errors:
        raise ImportRowsError(errors)

    added = 0
    for ticker, closes in closes_by_ticker(prices).items():
        added += insert_new_closes(db, security_ids[ticker], closes)
    db.commit()
    return added


def main() -> int:
    content = PRICE_HISTORY_FILE.read_bytes()
    try:
        with SessionLocal() as db:
            added = seed_prices(db, content, market_today())
    except ImportRowsError as error:
        for row_error in error.errors[:10]:
            print(f"Row {row_error.row}, {row_error.column}: {row_error.message}")
        print(f"{PRICE_HISTORY_FILE.name} has {len(error.errors)} invalid rows. Nothing was added.")
        return 1

    print(f"Added {added} prices from {PRICE_HISTORY_FILE.name}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
