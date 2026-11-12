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


DATABASE_URL = _use_psycopg_driver(_require("DATABASE_URL"))
