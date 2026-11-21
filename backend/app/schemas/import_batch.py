"""Response shapes for past imports."""

from datetime import datetime

from pydantic import BaseModel

from app.models import ImportBatch


class ImportBatchRead(BaseModel):
    """One imported file."""

    id: int
    file_name: str
    row_count: int
    # The name of the user who uploaded the file.
    imported_by: str
    created_at: datetime

    @classmethod
    def from_batch(cls, batch: ImportBatch) -> "ImportBatchRead":
        """Build the response from an ImportBatch whose user has been loaded."""
        return cls(
            id=batch.id,
            file_name=batch.file_name,
            row_count=batch.row_count,
            imported_by=batch.imported_by.name,
            created_at=batch.created_at,
        )
