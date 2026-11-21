"""Setup for the tests that run real queries against PostgreSQL.

They need TEST_DATABASE_URL and are skipped without it, except in CI, where
they fail. Every test runs
inside a transaction that is undone afterwards, so the tests leave no rows
behind and can run in any order.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

BACKEND_DIR = Path(__file__).resolve().parents[2]
TEST_DATABASE_SUFFIX = "_test"


def _run_alembic(*arguments: str) -> None:
    """Run an alembic command the way a developer would, against the test database."""
    result = subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.fixture(scope="session")
def alembic():
    return _run_alembic


@pytest.fixture(scope="session")
def migrated_engine():
    """The engine of the test database, with every migration applied."""
    if not os.environ["TEST_DATABASE_URL"]:
        # CI always has a database, so there a missing one is a mistake in the
        # workflow. Failing stops these tests from being skipped unnoticed.
        if os.environ.get("CI"):
            pytest.fail("TEST_DATABASE_URL is not set.")
        pytest.skip("TEST_DATABASE_URL is not set.")

    from app.database import engine

    # The migration tests drop every table, so a database with any other name is refused.
    if not (engine.url.database or "").endswith(TEST_DATABASE_SUFFIX):
        pytest.fail(f"TEST_DATABASE_URL must name a database ending in {TEST_DATABASE_SUFFIX}.")

    _run_alembic("upgrade", "head")
    return engine


@pytest.fixture
def db(migrated_engine):
    """A session whose changes are undone after the test, including the ones the code commits."""
    with migrated_engine.connect() as connection:
        transaction = connection.begin()
        # A commit made by the code under test ends a savepoint, not the transaction.
        session = Session(
            bind=connection,
            join_transaction_mode="create_savepoint",
            autoflush=False,
            expire_on_commit=False,
        )
        try:
            yield session
        finally:
            session.close()
            transaction.rollback()


@pytest.fixture
def save(db):
    """Save rows built by the factories, and return them with their ids filled in."""

    def save_rows(*rows):
        db.add_all(rows)
        db.flush()
        return rows[0] if len(rows) == 1 else rows

    return save_rows
