"""Create and read the signed token that keeps a user signed in. Uses no database."""

from datetime import datetime, timedelta

import jwt

from app.config import SESSION_MINUTES, jwt_secret

ALGORITHM = "HS256"


class InvalidTokenError(Exception):
    """Raised when a token is expired, changed, or was not signed by this app."""


def create_token(session_id: str, now: datetime, minutes: int = SESSION_MINUTES) -> str:
    """Return a token for the session that stops working after the given minutes."""
    claims = {"sub": session_id, "exp": now + timedelta(minutes=minutes)}
    return jwt.encode(claims, jwt_secret(), algorithm=ALGORITHM)


def read_token(token: str) -> str:
    """Return the session id inside a token. Raises InvalidTokenError if it cannot be trusted."""
    try:
        claims = jwt.decode(
            token,
            jwt_secret(),
            # Naming the algorithm stops a token that claims to need no signature.
            algorithms=[ALGORITHM],
            options={"require": ["sub", "exp"]},
        )
        return claims["sub"]
    except jwt.InvalidTokenError as error:
        raise InvalidTokenError("The token is not valid.") from error
