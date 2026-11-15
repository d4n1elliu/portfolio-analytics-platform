"""Fetch closing prices from Yahoo Finance."""

from datetime import date, timedelta

import yfinance

from app.services.price_provider import (
    DailyClose,
    ProviderError,
    closes_from_rows,
    to_provider_symbol,
)


class YahooPriceProvider:
    """A PriceProvider backed by Yahoo Finance."""

    def fetch_closes(self, ticker: str, start: date, end: date) -> list[DailyClose]:
        symbol = to_provider_symbol(ticker)
        try:
            history = yfinance.Ticker(symbol).history(
                start=start,
                # Yahoo leaves out the end date, so ask for one day more.
                end=end + timedelta(days=1),
                # Raw closes. Adjusted ones are rewritten after every dividend.
                auto_adjust=False,
            )
        except Exception as error:
            raise ProviderError(f"Yahoo could not return prices for {symbol}") from error

        if history.empty:
            return []
        return closes_from_rows(
            (timestamp.date(), float(close)) for timestamp, close in history["Close"].items()
        )
