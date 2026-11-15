"""Response shapes shared by more than one endpoint."""

from decimal import ROUND_HALF_UP, Decimal
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")

CENTS = Decimal("0.01")


def round_decimal(value: Decimal, places: Decimal) -> Decimal:
    """Round half up to the given places, such as CENTS."""
    return value.quantize(places, rounding=ROUND_HALF_UP)


class Page(BaseModel, Generic[T]):
    """One page of a list. Use it as Page[TradeRead], for example."""

    items: list[T]
    # Number of items in the whole list, not just on this page.
    total: int
    limit: int
    offset: int


class ImportResult(BaseModel):
    """Returned when a CSV import succeeds."""

    imported: int


class ImportRowError(BaseModel):
    """One problem found in an uploaded CSV. The header is row 1."""

    row: int
    column: str
    message: str


class ImportRejected(BaseModel):
    """Returned with status 422 when rows are invalid. Nothing was saved."""

    detail: str
    errors: list[ImportRowError]
