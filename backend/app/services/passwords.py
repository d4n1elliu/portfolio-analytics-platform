"""Hash passwords and check them. Uses no database."""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

MIN_PASSWORD_LENGTH = 12

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Return an Argon2 hash that is safe to store.

    Each call uses a new random salt, so the same password gives a different
    hash every time.
    """
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def password_problem(password: str) -> str | None:
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"The new password must be at least {MIN_PASSWORD_LENGTH} characters."
    return None
