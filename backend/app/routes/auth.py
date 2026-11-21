"""Endpoints for signing in and out."""

from datetime import UTC, datetime, timedelta
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.config import COOKIE_SECURE, SESSION_MINUTES
from app.database import get_db
from app.models import User, UserSession
from app.routes.dependencies import (
    SESSION_COOKIE,
    find_current_session,
    get_current_session,
    get_current_user,
)
from app.schemas.user import LoginRequest, PasswordChange, UserRead
from app.services import user_sessions as user_sessions_service
from app.services import users as users_service
from app.services.login_limiter import LoginLimiter
from app.services.passwords import password_problem
from app.services.tokens import create_token

router = APIRouter(prefix="/auth", tags=["auth"])

# How the session cookie is set and cleared. httponly keeps page scripts from
# reading it, and samesite stops other sites from sending it with a request.
COOKIE_SETTINGS = {"httponly": True, "secure": COOKIE_SECURE, "samesite": "lax", "path": "/"}

_login_limiter = LoginLimiter()


def get_login_limiter() -> LoginLimiter:
    """Give the login endpoint the one limiter the app shares. Use with Depends()."""
    return _login_limiter


@router.post("/login", response_model=UserRead)
def login(
    credentials: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    limiter: LoginLimiter = Depends(get_login_limiter),
):
    """Sign in with an email and password. Sets the session cookie."""
    now = datetime.now(UTC)
    address = _client_address(request)

    wait = limiter.retry_after(address, now)
    if wait is not None:
        raise _too_many_failures(wait)

    found = users_service.find_by_email(db, credentials.email)
    user = users_service.check_credentials(found, credentials.password)
    if user is None:
        limiter.record_failure(address, now)
        # One message for every failure, so it does not show which emails exist.
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password.")

    session = user_sessions_service.start_session(db, user, now)
    response.set_cookie(
        SESSION_COOKIE,
        create_token(session.id, now),
        max_age=SESSION_MINUTES * 60,
        **COOKIE_SETTINGS,
    )
    return UserRead.from_user(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    session: UserSession | None = Depends(find_current_session),
    db: Session = Depends(get_db),
):
    """Sign out by ending the session and clearing its cookie."""
    if session is not None:
        user_sessions_service.end_session(db, session, datetime.now(UTC))
    response.delete_cookie(SESSION_COOKIE, **COOKIE_SETTINGS)


@router.post("/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    change: PasswordChange,
    session: UserSession = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    """Set a new password, and sign the user out everywhere else."""
    if users_service.password_is_locked(session.user):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "The password of this account cannot be changed."
        )
    if users_service.check_credentials(session.user, change.current_password) is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The current password is incorrect.")
    problem = password_problem(change.new_password)
    if problem is not None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, problem)

    users_service.set_password(db, session.user, change.new_password)
    user_sessions_service.end_other_sessions(db, session, datetime.now(UTC))


@router.get("/me", response_model=UserRead)
def read_current_user(user: User = Depends(get_current_user)):
    """Return the signed-in user."""
    return UserRead.from_user(user)


def _too_many_failures(wait: timedelta) -> HTTPException:
    seconds = ceil(wait.total_seconds())
    minutes = ceil(seconds / 60)
    return HTTPException(
        status.HTTP_429_TOO_MANY_REQUESTS,
        f"Too many failed sign-ins. Try again in {minutes} "
        f"{'minute' if minutes == 1 else 'minutes'}.",
        headers={"Retry-After": str(seconds)},
    )


def _client_address(request: Request) -> str:
    """Return the visitor's address, for counting failed sign-ins.

    In production the request arrives through Caddy, which puts the visitor's
    address in X-Forwarded-For. Without that header it is a direct connection.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"
