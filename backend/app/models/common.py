"""Building blocks shared by the models.

Column types and columns that more than one table uses are defined once here,
so every table stores the same kind of value in the same way.
"""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

# Money and quantities are stored as exact decimals (Numeric), never Float,
# because Float cannot hold values such as 0.1 exactly and the rounding errors
# add up. Numeric(18, 6) allows 18 digits in total, 6 of them after the
# decimal point.

# A number of shares or units. Six decimal places allow fractional units.
QUANTITY = Numeric(18, 6)

# A price for one share or unit. Six decimal places cover prices quoted in
# fractions of a cent.
UNIT_PRICE = Numeric(18, 6)

# A cash amount in dollars and cents, such as a fee.
CASH_AMOUNT = Numeric(18, 2)


def one_of(column: str, values: type[StrEnum]) -> str:
    """Build the rule "column IN (...)" from an enum, for a CheckConstraint.

    The allowed values are then listed in one place. The database is only
    updated by a migration, so adding a value also needs a new migration that
    replaces the constraint.
    """
    return "{} IN ({})".format(column, ", ".join(f"'{value.value}'" for value in values))


class CreatedAtMixin:
    """Adds a created_at column that the database fills in on insert.

    Use it by listing it before Base: class Trade(CreatedAtMixin, Base).
    """

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
