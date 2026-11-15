"""Fetch a year of closing prices and write them to the price history CSV.

Run from the backend/ directory with:
    python -m jobs.export_price_history

The file is committed, so a new database can be given prices with no network
call. Run this again only to replace the history with a newer year.
"""

import csv
import sys
from datetime import timedelta

from app.config import PRICE_LOOKBACK_DAYS
from app.services.market_time import market_today
from app.services.price_csv import REQUIRED_COLUMNS
from jobs.seed_prices import PRICE_HISTORY_FILE
from jobs.yahoo_provider import YahooPriceProvider
from scripts.seed import SECURITIES


def main() -> int:
    provider = YahooPriceProvider()
    today = market_today()
    start = today - timedelta(days=PRICE_LOOKBACK_DAYS)

    rows = []
    for ticker in sorted(security["ticker"] for security in SECURITIES):
        closes = provider.fetch_closes(ticker, start, today)
        if not closes:
            print(f"No prices came back for {ticker}. The file was not written.")
            return 1
        rows.extend((close.price_date.isoformat(), ticker, str(close.close)) for close in closes)

    with PRICE_HISTORY_FILE.open("w", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(REQUIRED_COLUMNS)
        writer.writerows(sorted(rows))

    print(f"Wrote {len(rows)} prices to {PRICE_HISTORY_FILE.name}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
