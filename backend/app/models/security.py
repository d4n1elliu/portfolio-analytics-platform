"""Security model: an instrument the fund can hold, such as a share or an ETF."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import CreatedAtMixin

# These imports are needed only for the type hints on the relationships below.
# Importing them normally would make the model files import each other in a
# circle.
if TYPE_CHECKING:
    from app.models.price import Price
    from app.models.trade import Trade

DEFAULT_CURRENCY = "AUD"


class Security(CreatedAtMixin, Base):
    __tablename__ = "securities"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Exchange code, for example "BHP". Each security has a different one.
    ticker: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    # Industry group, for example "Materials". A fund that holds many
    # companies uses "Diversified".
    sector: Mapped[str] = mapped_column(String(100))
    # Type of instrument, for example "Equity" or "ETF".
    asset_class: Mapped[str] = mapped_column(String(50))
    # Three-letter code (ISO 4217) for the currency the security trades in.
    currency: Mapped[str] = mapped_column(
        String(3), default=DEFAULT_CURRENCY, server_default=DEFAULT_CURRENCY
    )

    trades: Mapped[list[Trade]] = relationship(back_populates="security")
    prices: Mapped[list[Price]] = relationship(back_populates="security")

    def __repr__(self) -> str:
        return f"<Security {self.ticker}>"
