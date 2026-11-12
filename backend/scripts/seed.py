"""Load the starting data into the database.

Run from the backend/ directory with:
    python -m scripts.seed

Safe to run more than once: rows that already exist are skipped, so no
duplicates are created.
"""

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Security

# Ten well-known ASX-listed securities. Sectors follow GICS, the industry
# classification the ASX uses. VAS is a fund that holds many companies, so it
# has no single sector. Currency is left out, so each row gets the default.
SECURITIES = [
    {"ticker": "BHP", "name": "BHP Group Limited", "sector": "Materials", "asset_class": "Equity"},
    {"ticker": "CBA", "name": "Commonwealth Bank of Australia", "sector": "Financials", "asset_class": "Equity"},
    {"ticker": "CSL", "name": "CSL Limited", "sector": "Health Care", "asset_class": "Equity"},
    {"ticker": "WES", "name": "Wesfarmers Limited", "sector": "Consumer Discretionary", "asset_class": "Equity"},
    {"ticker": "WOW", "name": "Woolworths Group Limited", "sector": "Consumer Staples", "asset_class": "Equity"},
    {"ticker": "TLS", "name": "Telstra Group Limited", "sector": "Communication Services", "asset_class": "Equity"},
    {"ticker": "NAB", "name": "National Australia Bank Limited", "sector": "Financials", "asset_class": "Equity"},
    {"ticker": "MQG", "name": "Macquarie Group Limited", "sector": "Financials", "asset_class": "Equity"},
    {"ticker": "RIO", "name": "Rio Tinto Limited", "sector": "Materials", "asset_class": "Equity"},
    {"ticker": "VAS", "name": "Vanguard Australian Shares Index ETF", "sector": "Diversified", "asset_class": "ETF"},
]


def seed_securities(session: Session, securities: list[dict[str, str]]) -> int:
    """Insert the given securities, skipping any whose ticker already exists.

    Returns the number of rows inserted. The caller is responsible for
    committing the session.
    """
    # ON CONFLICT DO NOTHING tells PostgreSQL to skip a row with a ticker that
    # is already in the table, instead of raising an error. RETURNING gives
    # back the tickers that were actually inserted.
    statement = (
        insert(Security)
        .values(securities)
        .on_conflict_do_nothing(index_elements=["ticker"])
        .returning(Security.ticker)
    )
    inserted_tickers = session.execute(statement).scalars().all()
    return len(inserted_tickers)


def main() -> None:
    """Run every seed step in one transaction and report what happened."""
    with SessionLocal() as session:
        inserted = seed_securities(session, SECURITIES)
        session.commit()
        total = session.scalar(select(func.count()).select_from(Security))

    skipped = len(SECURITIES) - inserted
    print(f"Securities: inserted {inserted}, skipped {skipped} already present.")
    print(f"The securities table now has {total} rows.")


if __name__ == "__main__":
    main()
