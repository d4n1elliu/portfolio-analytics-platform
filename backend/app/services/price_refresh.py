"""Fetch recent closing prices from a provider and store them."""

import logging
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import date, timedelta
from functools import partial

from sqlalchemy.orm import Session

from app.config import PRICE_LOOKBACK_DAYS, PRICE_REFRESH_OVERLAP_DAYS
from app.models import Security
from app.services.price_provider import DailyClose, PriceProvider
from app.services.prices import latest_price_dates, save_closes
from app.services.securities import list_securities

logger = logging.getLogger(__name__)

SaveCloses = Callable[[Security, list[DailyClose]], int]


@dataclass
class RefreshResult:
    attempted: int = 0
    saved: int = 0
    failed: list[str] = field(default_factory=list)

    @property
    def all_failed(self) -> bool:
        """True when every security failed. False when there were none."""
        return self.attempted > 0 and len(self.failed) == self.attempted


def refresh_prices(db: Session, provider: PriceProvider, today: date) -> RefreshResult:
    """Refresh the prices of every security in the database."""
    return refresh_securities(
        list_securities(db), latest_price_dates(db), provider, today, partial(_save_and_commit, db)
    )


def _save_and_commit(db: Session, security: Security, closes: list[DailyClose]) -> int:
    """Save one security's closes in their own transaction."""
    try:
        saved = save_closes(db, security.id, closes)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return saved


def refresh_securities(
    securities: Iterable[Security],
    latest_dates: Mapping[int, date],
    provider: PriceProvider,
    today: date,
    save: SaveCloses,
) -> RefreshResult:
    """Fetch and save the recent closes of each security. Uses no database itself.

    A security that fails is recorded and the rest carry on. No closes is not
    a failure, because there may have been no trading days.
    """
    result = RefreshResult()
    for security in securities:
        result.attempted += 1
        start, end = refresh_window(latest_dates.get(security.id), today)
        try:
            closes = provider.fetch_closes(security.ticker, start, end)
            if closes:
                result.saved += save(security, closes)
        except Exception:
            # Catch everything, so one bad security cannot stop the others.
            logger.exception("Could not refresh prices for %s", security.ticker)
            result.failed.append(security.ticker)
    return result


def refresh_window(
    latest_stored: date | None,
    today: date,
    overlap_days: int = PRICE_REFRESH_OVERLAP_DAYS,
    lookback_days: int = PRICE_LOOKBACK_DAYS,
) -> tuple[date, date]:
    """Return the first and last day to fetch for one security."""
    days_back = lookback_days if latest_stored is None else (today - latest_stored).days + overlap_days
    return today - timedelta(days=days_back), today
