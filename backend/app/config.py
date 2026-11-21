"""Application settings, read from environment variables.

This is the only file that loads backend/.env. Other files import the settings
they need from here, so this is the one place to see what the app needs in
order to run.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent

# Copies the values in backend/.env into environment variables. A variable
# that is already set (in the shell, or on a hosting platform) is left alone,
# so it takes priority over .env.
load_dotenv(BACKEND_DIR / ".env")

_PSYCOPG_SCHEME = "postgresql+psycopg://"


def _use_psycopg_driver(url: str) -> str:
    """Rewrite the start of a database URL so SQLAlchemy uses psycopg 3.

    The driver is the library that actually talks to PostgreSQL. This project
    installs psycopg 3, but a URL starting with postgresql:// makes SQLAlchemy
    look for the older psycopg2, and one starting with postgres:// is rejected.
    Rewriting both means a URL copied from Neon works without editing.
    """
    for scheme in ("postgresql://", "postgres://"):
        if url.startswith(scheme):
            return _PSYCOPG_SCHEME + url[len(scheme) :]
    return url


def _require(name: str) -> str:
    """Return an environment variable, or stop with a clear error if it is unset."""
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(
            f"{name} is not set. Copy backend/.env.example to backend/.env "
            f"and set {name}, or export it in your shell."
        )
    return value


def _optional_int(name: str, default: int) -> int:
    """Return an environment variable as a whole number, or the default if unset."""
    value = os.getenv(name, "").strip()
    return int(value) if value else default


def _optional_list(name: str, default: list[str]) -> list[str]:
    """Return a comma-separated environment variable as a list, or the default."""
    value = os.getenv(name, "").strip()
    return [item.strip() for item in value.split(",") if item.strip()] if value else default


DATABASE_URL = _use_psycopg_driver(_require("DATABASE_URL"))

# Web addresses allowed to call the API from a browser.
CORS_ORIGINS = _optional_list("CORS_ORIGINS", ["http://localhost:5173"])

# Time zone that decides what "today" is for trade dates.
MARKET_TIMEZONE = os.getenv("MARKET_TIMEZONE", "").strip() or "Australia/Sydney"

# Limits on uploaded CSV files.
IMPORT_MAX_FILE_BYTES = _optional_int("IMPORT_MAX_FILE_BYTES", 1024 * 1024)
IMPORT_MAX_ROWS = _optional_int("IMPORT_MAX_ROWS", 5000)

# A price refresh starts this many days before a security's latest stored
# price, or a full lookback ago when it has none.
PRICE_REFRESH_OVERLAP_DAYS = _optional_int("PRICE_REFRESH_OVERLAP_DAYS", 5)
PRICE_LOOKBACK_DAYS = _optional_int("PRICE_LOOKBACK_DAYS", 365)

PASSWORD_LOCKED_EMAILS = [email.lower() for email in _optional_list("PASSWORD_LOCKED_EMAILS", [])]

BENCHMARK_TICKER = os.getenv("BENCHMARK_TICKER", "").strip().upper() or "VAS"

# How long a sign in lasts before the user has to sign in again.
SESSION_MINUTES = _optional_int("SESSION_MINUTES", 480)


def jwt_secret() -> str:
    """Return the secret that signs session tokens.

    Read when a token is signed or checked, not when the app starts, so a job
    that never signs anyone in, such as the price refresh, runs without it.
    """
    return _require("JWT_SECRET")


def cookie_secure(origins: list[str]) -> bool:
    """Return True if the session cookie should be sent over HTTPS only.

    True when every allowed origin uses HTTPS, as in production. Local
    development runs on plain HTTP, where a secure cookie would not be sent.
    """
    return all(origin.startswith("https://") for origin in origins)


COOKIE_SECURE = cookie_secure(CORS_ORIGINS)

# Page sizes for endpoints that return lists.
DEFAULT_PAGE_SIZE = _optional_int("DEFAULT_PAGE_SIZE", 50)
MAX_PAGE_SIZE = _optional_int("MAX_PAGE_SIZE", 500)
