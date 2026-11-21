"""Reusable request handling for routes: paging, CSV uploads and the signed-in user."""

from dataclasses import dataclass
from enum import StrEnum

from fastapi import Cookie, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.config import DEFAULT_PAGE_SIZE, IMPORT_MAX_FILE_BYTES, MAX_PAGE_SIZE
from app.database import get_db
from app.models import Role, Security, User
from app.schemas.common import Page
from app.services import securities as securities_service
from app.services import users as users_service
from app.services.tokens import InvalidTokenError, read_token

CSV_EXTENSION = ".csv"
SESSION_COOKIE = "session"


@dataclass(frozen=True)
class PageParams:
    limit: int
    offset: int


@dataclass(frozen=True)
class CsvUpload:
    file_name: str
    content: bytes


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


def page_params(
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Items per page."),
    offset: int = Query(0, ge=0, description="Items to skip."),
) -> PageParams:
    """Read limit and offset from the query string. Use with Depends()."""
    return PageParams(limit=limit, offset=offset)


def page_of(items: list, total: int, page: PageParams) -> Page:
    """Build the response for one page of a list."""
    return Page(items=items, total=total, limit=page.limit, offset=page.offset)


def read_csv_upload(file: UploadFile) -> CsvUpload:
    """Return the name and contents of an uploaded CSV. Use with Depends().

    Rejects a file that is not a .csv (400) or is too large (413).
    """
    file_name = file.filename or ""
    if not file_name.lower().endswith(CSV_EXTENSION):
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
    return CsvUpload(file_name, content)


def get_current_user(
    token: str | None = Cookie(None, alias=SESSION_COOKIE), db: Session = Depends(get_db)
) -> User:
    """Return the signed-in user. Use with Depends().

    Answers 401 if there is no valid session, or the user is gone or inactive.
    """
    not_signed_in = HTTPException(status.HTTP_401_UNAUTHORIZED, "Sign in to continue.")
    try:
        user_id = read_token(token or "")
    except InvalidTokenError:
        raise not_signed_in from None

    user = users_service.find_by_id(db, user_id)
    if user is None or not user.is_active:
        raise not_signed_in
    return user


def get_security(ticker: str, db: Session = Depends(get_db)) -> Security:
    """Return the security named in the path. Use with Depends().

    Answers 404 if no security has that ticker.
    """
    security = securities_service.find_by_ticker(db, ticker)
    if security is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No security has the ticker '{ticker}'.")
    return security


def require_role(*allowed: Role):
    """Build a dependency that only lets the given roles through. Use with Depends().

    Answers 401 when nobody is signed in and 403 when the user's role is not allowed.
    """

    def check_role(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Your role does not allow this.")
        return user

    return check_role


def _format_size(size_bytes: int) -> str:
    megabytes = size_bytes / (1024 * 1024)
    return f"{megabytes:g} MB" if megabytes >= 1 else f"{size_bytes / 1024:g} KB"
