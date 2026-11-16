"""Endpoints for signing in and out."""

from datetime import UTC, datetime, timedelta
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.config import COOKIE_SECURE, SESSION_MINUTES
from app.database import get_db
from app.models import User
from app.routes.dependencies import SESSION_COOKIE, get_current_user
from app.schemas.user import LoginRequest, UserRead
from app.services import users as users_service
from app.services.login_limiter import LoginLimiter
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

    response.set_cookie(
        SESSION_COOKIE, create_token(user.id, now), max_age=SESSION_MINUTES * 60, **COOKIE_SETTINGS
    )
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    """Sign out by clearing the session cookie."""
    response.delete_cookie(SESSION_COOKIE, **COOKIE_SETTINGS)


@router.get("/me", response_model=UserRead)
def read_current_user(user: User = Depends(get_current_user)):
    """Return the signed-in user."""
    return user


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
