"""Find users and check their passwords."""

from functools import cache

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import PASSWORD_LOCKED_EMAILS
from app.models import User
from app.services.passwords import hash_password, verify_password


def find_by_email(db: Session, email: str) -> User | None:
    """Return the user with this email, ignoring capital letters and outer spaces."""
    return db.scalar(select(User).where(User.email == email.strip().lower()))


def check_credentials(user: User | None, password: str) -> User | None:
    """Return the user if the password is right and the account is active.

    Uses no database. Pass None when no user has the email that was entered.
    """
    # The password is checked even when there is no user, so the time taken
    # does not show whether an email exists.
    password_hash = user.password_hash if user else _placeholder_hash()
    password_matches = verify_password(password, password_hash)

    if user is None or not password_matches or not user.is_active:
        return None
    return user


@cache
def _placeholder_hash() -> str:
    return hash_password("a password that no account has")


def set_password(db: Session, user: User, password: str) -> None:
    user.password_hash = hash_password(password)
    db.commit()


def password_is_locked(user: User) -> bool:
    return user.email in PASSWORD_LOCKED_EMAILS
