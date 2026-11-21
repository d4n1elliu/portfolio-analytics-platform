"""Queries for reading trades."""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, contains_eager, joinedload

from app.models import Security, Trade, TradeSide


class TradeSort(StrEnum):
    """The columns a list of trades can be ordered by."""

    TRADE_DATE = "trade_date"
    TICKER = "ticker"
    SIDE = "side"
    QUANTITY = "quantity"
    PRICE = "price"
    FEES = "fees"


_SORT_COLUMNS = {
    TradeSort.TRADE_DATE: Trade.trade_date,
    TradeSort.TICKER: Security.ticker,
    TradeSort.SIDE: Trade.side,
    TradeSort.QUANTITY: Trade.quantity,
    TradeSort.PRICE: Trade.price,
    TradeSort.FEES: Trade.fees,
}


@dataclass(frozen=True)
class TradeQuery:
    """Which trades to return, and in what order. None means no filter."""

    # Upper case, matched exactly.
    ticker: str | None = None
    side: TradeSide | None = None
    # Both dates are included.
    date_from: date | None = None
    date_to: date | None = None
    sort: TradeSort = TradeSort.TRADE_DATE
    descending: bool = True


def list_trades_oldest_first(db: Session, up_to: date | None = None) -> list[Trade]:
    """Return every trade, with its security, oldest first.

    Give up_to to leave out the trades made after that date.
    """
    statement = (
        select(Trade)
        .options(joinedload(Trade.security))
        # The id decides the order of trades on the same day.
        .order_by(Trade.trade_date, Trade.id)
    )
    if up_to is not None:
        statement = statement.where(Trade.trade_date <= up_to)
    return list(db.scalars(statement))


def list_trades(db: Session, query: TradeQuery, limit: int, offset: int) -> tuple[list[Trade], int]:
    """Return one page of the matching trades, and how many match in total."""
    matching = _matching(query)
    total = db.scalar(select(func.count()).select_from(matching.subquery())) or 0
    page = _ordered(matching, query).limit(limit).offset(offset)
    return list(db.scalars(page)), total


def list_all_trades(db: Session, query: TradeQuery) -> list[Trade]:
    """Return every matching trade, with its security, in the order asked for."""
    return list(db.scalars(_ordered(_matching(query), query)))


def _matching(query: TradeQuery) -> Select:
    # One join both filters by ticker and loads each trade's security.
    statement = select(Trade).join(Trade.security).options(contains_eager(Trade.security))
    if query.ticker is not None:
        statement = statement.where(Security.ticker == query.ticker)
    if query.side is not None:
        statement = statement.where(Trade.side == query.side)
    if query.date_from is not None:
        statement = statement.where(Trade.trade_date >= query.date_from)
    if query.date_to is not None:
        statement = statement.where(Trade.trade_date <= query.date_to)
    return statement


def _ordered(statement: Select, query: TradeQuery) -> Select:
    column = _SORT_COLUMNS[query.sort]
    # The id breaks ties, so the order is the same on every page.
    if query.descending:
        return statement.order_by(column.desc(), Trade.id.desc())
    return statement.order_by(column, Trade.id)
