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

# Page sizes for endpoints that return lists.
DEFAULT_PAGE_SIZE = _optional_int("DEFAULT_PAGE_SIZE", 50)
MAX_PAGE_SIZE = _optional_int("MAX_PAGE_SIZE", 500)
