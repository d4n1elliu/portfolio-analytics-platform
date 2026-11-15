"""Fetch the latest closing prices and store them.

Run from the backend/ directory with:
    python -m jobs.refresh_prices

Safe to run more than once: a price already stored for a day is replaced.
"""

import logging
import sys

from app.database import SessionLocal
from app.services.market_time import market_today
from app.services.price_refresh import refresh_prices
from jobs.yahoo_provider import YahooPriceProvider

logger = logging.getLogger(__name__)


def main() -> int:
    """Refresh every security. Returns 1 only if all of them failed."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    with SessionLocal() as db:
        result = refresh_prices(db, YahooPriceProvider(), market_today())

    logger.info(
        "Refreshed %d securities: %d prices saved, %d failed.",
        result.attempted,
        result.saved,
        len(result.failed),
    )
    if result.failed:
        logger.warning("Failed: %s", ", ".join(result.failed))
    return 1 if result.all_failed else 0


if __name__ == "__main__":
    sys.exit(main())
