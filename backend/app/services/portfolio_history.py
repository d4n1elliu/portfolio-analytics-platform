"""The value of the portfolio on each past date, calculated from the trades and prices."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Price, Trade
from app.services.positions import ZERO, Position, calculate_position
from app.services.prices import list_prices_of_traded_securities
from app.services.trades import list_trades_oldest_first
from app.services.valuation import value_position


@dataclass(frozen=True)
class HistoryPoint:
    """The open positions at the end of one date, added up. Values are not rounded."""

    as_of: date
    market_value: Decimal
    cost_basis: Decimal
    unrealised_pnl: Decimal


def list_portfolio_history(db: Session) -> list[HistoryPoint]:
    """Return one point per priced date, oldest first."""
    return build_portfolio_history(list_trades_oldest_first(db), list_prices_of_traded_securities(db))


def build_portfolio_history(trades: Iterable[Trade], prices: Iterable[Price]) -> list[HistoryPoint]:
    """Value the portfolio on every date that has a price. Uses no database.

    The trades must be given oldest first. The prices can be in any order.
    The first point is the first priced date on which something is held.

    A trade counts from the first priced date on or after its trade date, so
    a weekend trade shows up on the next priced date. A security with no close
    on a date is valued at its most recent earlier close. A security with no
    close yet is left out of both the market value and the cost basis.
    """
    trades = list(trades)
    prices_by_date = _group_by_date(prices)

    trades_so_far: dict[str, list[Trade]] = {}
    positions: dict[str, Position] = {}
    latest_price: dict[str, Price] = {}
    next_trade = 0
    points = []

    for day in sorted(prices_by_date):
        for price in prices_by_date[day]:
            latest_price[price.security.ticker] = price

        # Only a position with a new trade is recalculated.
        traded = set()
        while next_trade < len(trades) and trades[next_trade].trade_date <= day:
            ticker = trades[next_trade].security.ticker
            trades_so_far.setdefault(ticker, []).append(trades[next_trade])
            traded.add(ticker)
            next_trade += 1
        for ticker in traded:
            positions[ticker] = calculate_position(trades_so_far[ticker])

        open_positions = {
            ticker: position for ticker, position in positions.items() if position.is_open
        }
        if points or open_positions:
            points.append(_point(day, open_positions, latest_price))
    return points


def _group_by_date(prices: Iterable[Price]) -> dict[date, list[Price]]:
    prices_by_date: dict[date, list[Price]] = {}
    for price in prices:
        prices_by_date.setdefault(price.price_date, []).append(price)
    return prices_by_date


def _point(
    day: date, open_positions: dict[str, Position], latest_price: dict[str, Price]
) -> HistoryPoint:
    """Add up the open positions that have a price."""
    market_value = ZERO
    cost_basis = ZERO
    for ticker, position in open_positions.items():
        price = latest_price.get(ticker)
        if price is None:
            continue
        market_value += value_position(position, price.close, price.price_date).market_value
        cost_basis += position.cost_basis
    return HistoryPoint(day, market_value, cost_basis, market_value - cost_basis)
