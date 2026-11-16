"""The value of the portfolio on each past date, calculated from the trades and prices."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Price, Trade, TradeSide
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
    # Cash put into the valued positions that day, less cash taken out. A buy
    # puts in its cost and fees. A sell takes out its proceeds after fees.
    net_flow: Decimal


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
    # Held on the previous date with no close yet, so not yet in the market value.
    unpriced: set[str] = set()
    next_trade = 0
    points = []

    for day in sorted(prices_by_date):
        for price in prices_by_date[day]:
            latest_price[price.security.ticker] = price

        # Only a position with a new trade is recalculated.
        cash_traded: dict[str, Decimal] = {}
        while next_trade < len(trades) and trades[next_trade].trade_date <= day:
            trade = trades[next_trade]
            ticker = trade.security.ticker
            trades_so_far.setdefault(ticker, []).append(trade)
            cash_traded[ticker] = cash_traded.get(ticker, ZERO) + _cash_flow(trade)
            next_trade += 1
        for ticker in cash_traded:
            positions[ticker] = calculate_position(trades_so_far[ticker])

        open_positions = {
            ticker: position for ticker, position in positions.items() if position.is_open
        }
        if points or open_positions:
            net_flow = _net_flow(cash_traded, open_positions, latest_price, unpriced)
            points.append(_point(day, open_positions, latest_price, net_flow))
        unpriced = {ticker for ticker in open_positions if ticker not in latest_price}
    return points


def _cash_flow(trade: Trade) -> Decimal:
    """Cash a trade puts into the portfolio. Negative for a sell, which takes cash out."""
    amount = trade.quantity * trade.price
    return amount + trade.fees if trade.side == TradeSide.BUY else trade.fees - amount


def _net_flow(
    cash_traded: dict[str, Decimal],
    open_positions: dict[str, Position],
    latest_price: dict[str, Price],
    unpriced: set[str],
) -> Decimal:
    """Add up the cash that went into the valued positions on one date.

    A position held with no close is not in the market value. On the date it
    gets its first close, its whole value counts as cash put in, so its
    arrival does not look like a gain.
    """
    newly_priced = {ticker for ticker in unpriced if ticker in latest_price}
    net_flow = sum(
        (
            cash
            for ticker, cash in cash_traded.items()
            if ticker in latest_price and ticker not in newly_priced
        ),
        ZERO,
    )
    for ticker in newly_priced & open_positions.keys():
        net_flow += _market_value(open_positions[ticker], latest_price[ticker])
    return net_flow


def _group_by_date(prices: Iterable[Price]) -> dict[date, list[Price]]:
    prices_by_date: dict[date, list[Price]] = {}
    for price in prices:
        prices_by_date.setdefault(price.price_date, []).append(price)
    return prices_by_date


def _point(
    day: date,
    open_positions: dict[str, Position],
    latest_price: dict[str, Price],
    net_flow: Decimal,
) -> HistoryPoint:
    """Add up the open positions that have a price."""
    market_value = ZERO
    cost_basis = ZERO
    for ticker, position in open_positions.items():
        price = latest_price.get(ticker)
        if price is None:
            continue
        market_value += _market_value(position, price)
        cost_basis += position.cost_basis
    return HistoryPoint(day, market_value, cost_basis, market_value - cost_basis, net_flow)


def _market_value(position: Position, price: Price) -> Decimal:
    return value_position(position, price.close, price.price_date).market_value
