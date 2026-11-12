"""Dates in the market's time zone, so results don't depend on the server's."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.config import MARKET_TIMEZONE


def market_today() -> date:
    """Today's date where the securities trade."""
    return datetime.now(ZoneInfo(MARKET_TIMEZONE)).date()
