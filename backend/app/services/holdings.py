"""Current positions, calculated from the trades. Nothing is stored."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Price, Security, Trade
from app.services.positions import Position, calculate_position
from app.services.prices import latest_prices
from app.services.trades import list_trades_oldest_first
from app.services.valuation import Valuation, portfolio_weights, value_position


@dataclass(frozen=True)
class Holding:
    security: Security
    position: Position
    # None when the position is closed or the security has no stored price.
    valuation: Valuation | None = None
    # Share of the total market value.
    weight: Decimal | None = None


def list_holdings(db: Session, include_closed: bool) -> list[Holding]:
    """Return the position in every traded security, ordered by ticker."""
    return build_holdings(list_trades_oldest_first(db), include_closed, latest_prices(db))


def build_holdings(
    trades: Iterable[Trade],
    include_closed: bool,
    prices: Mapping[str, Price] | None = None,
) -> list[Holding]:
    """Group trades by security, then calculate and value each position. Uses no database.

    The trades must be given oldest first, and prices holds the latest price
    by ticker. An oversold position is always included, because it means the
    trades are wrong.
    """
    prices = prices or {}
    trades_by_ticker: dict[str, list[Trade]] = {}
    for trade in trades:
        trades_by_ticker.setdefault(trade.security.ticker, []).append(trade)

    holdings = []
    for ticker in sorted(trades_by_ticker):
        security_trades = trades_by_ticker[ticker]
        position = calculate_position(security_trades)
        if position.is_open or include_closed or position.oversold_quantity > 0:
            valuation = _value(position, prices.get(ticker))
            holdings.append(Holding(security_trades[0].security, position, valuation))
    return _with_weights(holdings)


def _value(position: Position, price: Price | None) -> Valuation | None:
    if price is None or not position.is_open:
        return None
    return value_position(position, price.close, price.price_date)


def _with_weights(holdings: list[Holding]) -> list[Holding]:
    """Set the weight of every holding that has a valuation."""
    weights = portfolio_weights(
        {
            holding.security.ticker: holding.valuation.market_value
            for holding in holdings
            if holding.valuation is not None
        }
    )
    return [
        Holding(
            holding.security,
            holding.position,
            holding.valuation,
            weights.get(holding.security.ticker),
        )
        for holding in holdings
    ]
