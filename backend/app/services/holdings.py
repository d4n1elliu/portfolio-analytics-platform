"""Current positions, calculated from the trades. Nothing is stored."""

from collections.abc import Iterable
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Security, Trade
from app.services.positions import Position, calculate_position


@dataclass(frozen=True)
class Holding:
    security: Security
    position: Position


def list_holdings(db: Session, include_closed: bool) -> list[Holding]:
    """Return the position in every traded security, ordered by ticker."""
    statement = (
        select(Trade)
        .options(joinedload(Trade.security))
        # Oldest first. The id decides the order of trades on the same day.
        .order_by(Trade.trade_date, Trade.id)
    )
    return build_holdings(db.scalars(statement), include_closed)


def build_holdings(trades: Iterable[Trade], include_closed: bool) -> list[Holding]:
    """Group trades by security and calculate each position. Uses no database.

    The trades must be given oldest first. Closed positions are left out
    unless include_closed is set. An oversold position is always included,
    because it means the trades are wrong.
    """
    trades_by_ticker: dict[str, list[Trade]] = {}
    for trade in trades:
        trades_by_ticker.setdefault(trade.security.ticker, []).append(trade)

    holdings = []
    for ticker in sorted(trades_by_ticker):
        security_trades = trades_by_ticker[ticker]
        position = calculate_position(security_trades)
        if position.is_open or include_closed or position.oversold_quantity > 0:
            holdings.append(Holding(security_trades[0].security, position))
    return holdings
