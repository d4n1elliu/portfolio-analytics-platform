"""ImportBatch model: one uploaded file of trades, and who imported it."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import CreatedAtMixin

if TYPE_CHECKING:
    from app.models.user import User

FILE_NAME_LENGTH = 255


class ImportBatch(CreatedAtMixin, Base):
    __tablename__ = "import_batches"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(String(FILE_NAME_LENGTH))
    # SHA-256 of the file's bytes, as 64 hex characters. Unique, so the same
    # file cannot be imported twice.
    file_hash: Mapped[str] = mapped_column(String(64), unique=True)
    row_count: Mapped[int] = mapped_column(Integer)
    imported_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    imported_by: Mapped[User] = relationship()

    def __repr__(self) -> str:
        return f"<ImportBatch {self.file_name}: {self.row_count} rows>"
