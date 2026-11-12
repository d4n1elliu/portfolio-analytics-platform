"""Response shapes for trades."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models import Trade, TradeSide


class TradeRead(BaseModel):
    """A trade with details of its security.

    Decimals are sent as JSON strings such as "45.250000" to keep precision.
    """

    id: int
    trade_date: date
    ticker: str
    security_name: str
    currency: str
    side: TradeSide
    quantity: Decimal
    price: Decimal
    fees: Decimal
    created_at: datetime

    @classmethod
    def from_trade(cls, trade: Trade) -> "TradeRead":
        """Build the response from a Trade whose security has been loaded."""
        return cls(
            id=trade.id,
            trade_date=trade.trade_date,
            ticker=trade.security.ticker,
            security_name=trade.security.name,
            currency=trade.security.currency,
            side=TradeSide(trade.side),
            quantity=trade.quantity,
            price=trade.price,
            fees=trade.fees,
            created_at=trade.created_at,
        )
