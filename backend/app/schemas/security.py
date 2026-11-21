"""Response shapes for securities."""

import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models import Price


class SecurityRead(BaseModel):
    """A security as returned by the API."""

    # Lets this be built from a Security model object.
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticker: str
    name: str
    sector: str
    asset_class: str
    currency: str


class PriceRead(BaseModel):
    """The closing price of a security on one day. Sent as a JSON string to keep precision."""

    date: datetime.date
    close: Decimal

    @classmethod
    def from_price(cls, price: Price) -> "PriceRead":
        return cls(date=price.price_date, close=price.close)
