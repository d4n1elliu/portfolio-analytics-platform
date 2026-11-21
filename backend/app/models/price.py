"""Price model: the closing price of a security on one day."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import UNIT_PRICE

if TYPE_CHECKING:
    from app.models.security import Security


class Price(Base):
    __tablename__ = "prices"
    __table_args__ = (
        # A security can have only one closing price per day. PostgreSQL
        # enforces this with an index, which also makes it fast to look up the
        # prices for one security.
        UniqueConstraint("security_id", "price_date", name="uq_prices_security_id_price_date"),
        CheckConstraint("close > 0", name="close_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    security_id: Mapped[int] = mapped_column(ForeignKey("securities.id"))
    price_date: Mapped[date] = mapped_column(Date)
    # Stored with the same type as Trade.price, so the two compare exactly.
    close: Mapped[Decimal] = mapped_column(UNIT_PRICE)

    security: Mapped[Security] = relationship(back_populates="prices")

    def __repr__(self) -> str:
        return f"<Price security {self.security_id} on {self.price_date}: {self.close}>"
