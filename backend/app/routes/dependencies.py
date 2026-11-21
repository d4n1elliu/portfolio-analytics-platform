"""Reusable request handling for routes: paging, CSV uploads and the signed-in user."""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from fastapi import Cookie, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.ai import research
from app.ai import usage as ai_usage
from app.ai.usage import Allowance
from app.config import (
    AI_ENABLED,
    DEFAULT_PAGE_SIZE,
    IMPORT_MAX_FILE_BYTES,
    MAX_PAGE_SIZE,
    RESEARCH_MAX_FILE_BYTES,
)
from app.database import get_db
from app.models import Security, User, UserSession
from app.schemas.common import Page
from app.services import securities as securities_service
from app.services import user_sessions as user_sessions_service
from app.services.permissions import Permission, permissions_of
from app.services.tokens import InvalidTokenError, read_token

CSV_EXTENSION = ".csv"
SESSION_COOKIE = "session"


@dataclass(frozen=True)
class PageParams:
    limit: int
    offset: int


@dataclass(frozen=True)
class UploadedFile:
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


def read_csv_upload(file: UploadFile) -> UploadedFile:
    """Return the name and contents of an uploaded CSV. Use with Depends().

    Rejects a file that is not a .csv (400) or is too large (413).
    """
    return _read_upload(file, (CSV_EXTENSION,), IMPORT_MAX_FILE_BYTES)


def read_research_upload(file: UploadFile) -> UploadedFile:
    return _read_upload(file, research.FILE_TYPES, RESEARCH_MAX_FILE_BYTES)


def _read_upload(file: UploadFile, extensions: tuple[str, ...], max_bytes: int) -> UploadedFile:
    file_name = file.filename or ""
    if not file_name.lower().endswith(extensions):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, f"The file must be a {' or '.join(extensions)} file."
        )

    # Reading one byte past the limit shows the file is too big without
    # loading all of it.
    content = file.file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(
            status.HTTP_413_CONTENT_TOO_LARGE,
            f"The file is larger than {_format_size(max_bytes)}.",
        )
    return UploadedFile(file_name, content)


def find_current_session(
    token: str | None = Cookie(None, alias=SESSION_COOKIE), db: Session = Depends(get_db)
) -> UserSession | None:
    try:
        session_id = read_token(token or "")
    except InvalidTokenError:
        return None
    return user_sessions_service.find_active_session(db, session_id, datetime.now(UTC))


def get_current_session(
    session: UserSession | None = Depends(find_current_session),
) -> UserSession:
    if session is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sign in to continue.")
    return session


def get_current_user(session: UserSession = Depends(get_current_session)) -> User:
    """Return the signed-in user. Use with Depends().

    Answers 401 if there is no session, it has ended, or the user is inactive.
    """
    return session.user


def get_security(ticker: str, db: Session = Depends(get_db)) -> Security:
    """Return the security named in the path. Use with Depends().

    Answers 404 if no security has that ticker.
    """
    security = securities_service.find_by_ticker(db, ticker)
    if security is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No security has the ticker '{ticker}'.")
    return security


def require_ai_enabled() -> None:
    if not AI_ENABLED:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "The AI features are not turned on.")


def get_ai_allowance(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Allowance:
    return ai_usage.read_allowance(db, user, datetime.now(UTC))


def require_ai_allowance(allowance: Allowance = Depends(get_ai_allowance)) -> Allowance:
    if allowance.limit_reached is not None:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, allowance.limit_reached)
    return allowance


def require_permission(permission: Permission):
    """Build a dependency that only lets through roles with the permission. Use with Depends().

    Answers 401 when nobody is signed in and 403 when the user's role is not allowed.
    """

    def check_permission(user: User = Depends(get_current_user)) -> User:
        if permission not in permissions_of(user.role):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Your role does not allow this.")
        return user

    return check_permission


def _format_size(size_bytes: int) -> str:
    megabytes = size_bytes / (1024 * 1024)
    return f"{megabytes:g} MB" if megabytes >= 1 else f"{size_bytes / 1024:g} KB"
