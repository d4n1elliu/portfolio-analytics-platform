"""Tools for reading and checking any uploaded CSV file.

Nothing here is specific to trades or uses the database, so other imports
(such as prices) can reuse it.
"""

import csv
import io
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import TypeVar

from sqlalchemy import Numeric

DATE_FORMAT = "%Y-%m-%d"
DATE_FORMAT_LABEL = "YYYY-MM-DD"

# Digits with an optional decimal part, such as "100" or "45.25".
_PLAIN_NUMBER = re.compile(r"-?\d+(\.\d+)?")

# One row of a CSV file: its row number and its values by column name.
Row = tuple[int, dict[str, str]]
T = TypeVar("T")


@dataclass(frozen=True)
class RowError:
    """One problem found in a row. The header is row 1."""

    row: int
    column: str
    message: str


class ImportFileError(Exception):
    """The file as a whole cannot be imported."""


class ImportDuplicateError(Exception):
    """The same file was imported before."""


class ImportRowsError(Exception):
    """The file was readable but one or more rows broke a rule."""

    def __init__(self, errors: list[RowError]) -> None:
        super().__init__(f"{len(errors)} row errors")
        self.errors = errors


class RowErrors:
    """Collects the errors found while checking one row."""

    def __init__(self, row_number: int) -> None:
        self.row_number = row_number
        self.errors: list[RowError] = []

    def add(self, column: str, message: str) -> None:
        self.errors.append(RowError(self.row_number, column, message))


def decode_csv(content: bytes) -> str:
    """Turn uploaded bytes into text."""
    try:
        # utf-8-sig also removes the hidden marker Excel adds to CSV files.
        return content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ImportFileError("The file is not valid UTF-8 text.") from None


def read_rows(text: str, required_columns: tuple[str, ...], max_rows: int) -> list[Row]:
    """Split CSV text into rows, each with its row number in the file.

    Column names are lower-cased and values are trimmed. Raises
    ImportFileError if the file cannot be used.
    """
    reader = csv.reader(io.StringIO(text))
    header = next(reader, None)
    if header is None:
        raise ImportFileError("The file is empty.")

    columns = [name.strip().lower() for name in header]
    missing = [name for name in required_columns if name not in columns]
    if missing:
        raise ImportFileError(f"The header row is missing required columns: {', '.join(missing)}.")

    rows: list[Row] = []
    for values in reader:
        if not any(value.strip() for value in values):
            continue  # Blank line.
        if len(rows) == max_rows:
            raise ImportFileError(f"The file has more than {max_rows} rows.")
        row = {name: value.strip() for name, value in zip(columns, values)}
        rows.append((reader.line_num, row))

    if not rows:
        raise ImportFileError("The file has a header row but no data rows.")
    return rows


def validate_all(
    rows: list[Row],
    validate: Callable[[dict[str, str], int], tuple[T | None, list[RowError]]],
) -> tuple[list[T], list[RowError]]:
    """Run a row validator over every row and gather the results and errors."""
    items: list[T] = []
    errors: list[RowError] = []
    for row_number, row in rows:
        item, row_errors = validate(row, row_number)
        if item is not None:
            items.append(item)
        errors.extend(row_errors)
    return items, errors


# Each parser below returns the converted value, or records an error and
# returns None.


def parse_date(value: str, column: str, today: date, errors: RowErrors) -> date | None:
    """Parse a date that must not be in the future."""
    if not value:
        errors.add(column, f"{column} is required.")
        return None
    try:
        parsed = datetime.strptime(value, DATE_FORMAT).date()
    except ValueError:
        errors.add(column, f"'{value}' is not a valid date. Use {DATE_FORMAT_LABEL}.")
        return None
    if parsed > today:
        errors.add(column, f"{value} is in the future.")
        return None
    return parsed


def parse_ticker(value: str, column: str, known_tickers: set[str], errors: RowErrors) -> str | None:
    """Parse a ticker that must be one of known_tickers (upper case)."""
    if not value:
        errors.add(column, f"{column} is required.")
        return None
    ticker = value.upper()
    if ticker not in known_tickers:
        errors.add(column, f"'{value}' is not a known security.")
        return None
    return ticker


def parse_decimal(
    value: str,
    column: str,
    column_type: Numeric,
    errors: RowErrors,
    allow_zero: bool = False,
) -> Decimal | None:
    """Parse a positive number that fits the given database column type.

    Uses Decimal, not float, so the value is kept exactly as written.
    """
    if not value:
        errors.add(column, f"{column} is required.")
        return None
    if not _PLAIN_NUMBER.fullmatch(value):
        errors.add(column, f"'{value}' is not a number.")
        return None

    number = Decimal(value)
    if number < 0 or (number == 0 and not allow_zero):
        rule = "0 or more" if allow_zero else "greater than 0"
        errors.add(column, f"{column} must be {rule}.")
        return None

    # Reject a value the column would round, rather than saving a different one.
    decimal_places = -number.as_tuple().exponent
    if decimal_places > column_type.scale:
        errors.add(column, f"{column} can have at most {column_type.scale} decimal places.")
        return None
    if number >= Decimal(10) ** (column_type.precision - column_type.scale):
        errors.add(column, f"{column} is too large.")
        return None
    return number
