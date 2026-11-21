"""Turns import errors raised by services into HTTP responses.

Registered once in main.py, so every import endpoint answers the same way.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.schemas.common import ImportRejected, ImportRowError
from app.services.csv_parsing import ImportFileError, ImportRowsError

# Describes the error responses in the API docs. Pass to a route's "responses".
IMPORT_ERROR_RESPONSES = {
    400: {"description": "The file is not a readable CSV for this import."},
    413: {"description": "The file is too large."},
    422: {"model": ImportRejected, "description": "One or more rows are invalid."},
}


def _file_error(request: Request, error: ImportFileError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(error)})


def _rows_error(request: Request, error: ImportRowsError) -> JSONResponse:
    count = len(error.errors)
    body = ImportRejected(
        detail=(
            "The import was rejected and nothing was saved. "
            f"Fix {count} {'error' if count == 1 else 'errors'} and upload the file again."
        ),
        errors=[
            ImportRowError(row=e.row, column=e.column, message=e.message) for e in error.errors
        ],
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content=body.model_dump()
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ImportFileError, _file_error)
    app.add_exception_handler(ImportRowsError, _rows_error)
