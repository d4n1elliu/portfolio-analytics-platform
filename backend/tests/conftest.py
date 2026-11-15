"""Test setup. pytest runs this file before it collects any tests."""

import os

import pytest

# app.config requires DATABASE_URL. A placeholder lets the tests run without
# a .env file. Nothing connects to it: creating the engine does not open a
# connection, and no test runs a query. A value already set in the shell is
# kept, and an empty one counts as unset.
if not os.environ.get("DATABASE_URL", "").strip():
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"

# A made-up secret for signing tokens, so the tests never use a real one.
os.environ["JWT_SECRET"] = "test-secret-that-is-long-enough-for-hs256"


class FakeSession:
    """Stands in for the database session. Returns trades or prices to match the query."""

    def __init__(self, trades, prices):
        self.trades = trades
        self.prices = prices

    def scalars(self, statement):
        from app.models import Price

        asks_for_prices = statement.column_descriptions[0]["entity"] is Price
        return self.prices if asks_for_prices else self.trades


@pytest.fixture
def client_with_data():
    """Make a test client whose database holds the given trades and prices."""
    # Imported here because the app needs DATABASE_URL, which is set above.
    from fastapi.testclient import TestClient

    from app.database import get_db
    from app.main import app

    def make_client(trades, prices=None):
        app.dependency_overrides[get_db] = lambda: FakeSession(trades, prices or [])
        return TestClient(app)

    yield make_client
    app.dependency_overrides.clear()
