"""Reusable request handling for routes: paging and CSV uploads."""

from dataclasses import dataclass

from fastapi import HTTPException, Query, UploadFile, status

from app.config import DEFAULT_PAGE_SIZE, IMPORT_MAX_FILE_BYTES, MAX_PAGE_SIZE

CSV_EXTENSION = ".csv"


@dataclass(frozen=True)
class PageParams:
    limit: int
    offset: int


def page_params(
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Items per page."),
    offset: int = Query(0, ge=0, description="Items to skip."),
) -> PageParams:
    """Read limit and offset from the query string. Use with Depends()."""
    return PageParams(limit=limit, offset=offset)


def read_csv_upload(file: UploadFile) -> bytes:
    """Return the contents of an uploaded CSV. Use with Depends().

    Rejects a file that is not a .csv (400) or is too large (413).
    """
    if not (file.filename or "").lower().endswith(CSV_EXTENSION):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, f"The file must be a {CSV_EXTENSION} file."
        )

    # Reading one byte past the limit shows the file is too big without
    # loading all of it.
    content = file.file.read(IMPORT_MAX_FILE_BYTES + 1)
    if len(content) > IMPORT_MAX_FILE_BYTES:
        raise HTTPException(
            status.HTTP_413_CONTENT_TOO_LARGE,
            f"The file is larger than {_format_size(IMPORT_MAX_FILE_BYTES)}.",
        )
    return content


def _format_size(size_bytes: int) -> str:
    megabytes = size_bytes / (1024 * 1024)
    return f"{megabytes:g} MB" if megabytes >= 1 else f"{size_bytes / 1024:g} KB"
