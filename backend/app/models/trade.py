"""Trade model: one buy or sell of a security.

The trades table is the ledger. There is no holdings table: the current
position in a security is calculated by adding up its trades. That keeps the
ledger as the single source of truth, so a stored position can never disagree
with it.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import CASH_AMOUNT, QUANTITY, UNIT_PRICE, CreatedAtMixin, one_of

if TYPE_CHECKING:
    from app.models.security import Security


class TradeSide(StrEnum):
    """The two directions a trade can have.

    Use these instead of typing "BUY" or "SELL" by hand, for example
    Trade(side=TradeSide.BUY). Each member is also a plain string.
    """

    BUY = "BUY"
    SELL = "SELL"


class Trade(CreatedAtMixin, Base):
    __tablename__ = "trades"
    # Rules the database checks on every row, whichever code inserts it.
    __table_args__ = (
        CheckConstraint(one_of("side", TradeSide), name="side_valid"),
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("price > 0", name="price_positive"),
        CheckConstraint("fees >= 0", name="fees_not_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    security_id: Mapped[int] = mapped_column(ForeignKey("securities.id"), index=True)
    trade_date: Mapped[date] = mapped_column(Date, index=True)
    # A TradeSide value. The direction is recorded here, so quantity is always
    # a positive number.
    side: Mapped[str] = mapped_column(String(4))
    quantity: Mapped[Decimal] = mapped_column(QUANTITY)
    # Price paid or received for one unit, in the security's currency.
    price: Mapped[Decimal] = mapped_column(UNIT_PRICE)
    # Brokerage and other costs for the whole trade.
    fees: Mapped[Decimal] = mapped_column(
        CASH_AMOUNT, default=Decimal("0"), server_default="0"
    )

    security: Mapped[Security] = relationship(back_populates="trades")

    def __repr__(self) -> str:
        return f"<Trade {self.side} {self.quantity} of security {self.security_id}>"
