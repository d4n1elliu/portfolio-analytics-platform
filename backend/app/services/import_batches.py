"""Queries for reading past imports."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import ImportBatch


def find_by_hash(db: Session, file_hash: str) -> ImportBatch | None:
    statement = (
        select(ImportBatch)
        .options(joinedload(ImportBatch.imported_by))
        .where(ImportBatch.file_hash == file_hash)
    )
    return db.scalar(statement)


def list_import_batches(db: Session, limit: int, offset: int) -> tuple[list[ImportBatch], int]:
    total = db.scalar(select(func.count()).select_from(ImportBatch)) or 0
    statement = (
        select(ImportBatch)
        .options(joinedload(ImportBatch.imported_by))
        .order_by(ImportBatch.created_at.desc(), ImportBatch.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(statement)), total
