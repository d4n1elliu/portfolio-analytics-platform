"""Insert rows without failing on the ones that already exist."""

from collections.abc import Sequence
from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import InstrumentedAttribute, Session


def insert_missing(
    db: Session,
    model: type,
    rows: Sequence[dict[str, Any]],
    unique_columns: Sequence[str],
    returning: InstrumentedAttribute,
) -> list:
    """Insert the rows, skipping any that match an existing row on the unique columns.

    Returns the given column for each row that was inserted. The caller commits.
    """
    # ON CONFLICT DO NOTHING tells PostgreSQL to skip a clashing row instead of
    # raising an error. RETURNING gives back only the rows actually inserted.
    statement = (
        insert(model)
        .values(rows)
        .on_conflict_do_nothing(index_elements=unique_columns)
        .returning(returning)
    )
    return list(db.execute(statement).scalars())
