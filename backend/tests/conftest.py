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
    """Stands in for the database session. Returns the rows that match the query."""

    def __init__(self, trades=(), prices=(), users=()):
        self.trades = trades
        self.prices = prices
        self.users = users

    def scalars(self, statement):
        from app.models import Price

        asks_for_prices = statement.column_descriptions[0]["entity"] is Price
        return self.prices if asks_for_prices else self.trades

    def scalar(self, statement):
        """Return the user whose columns equal the values in the query, such as an email."""
        wanted = {
            name.rsplit("_", 1)[0]: value for name, value in statement.compile().params.items()
        }
        for user in self.users:
            if all(getattr(user, column) == value for column, value in wanted.items()):
                return user
        return None


def _client(session: FakeSession):
    """Make a test client that uses the given session instead of a database."""
    # Imported here because the app needs DATABASE_URL, which is set above.
    from fastapi.testclient import TestClient

    from app.database import get_db
    from app.main import app
    from app.routes.auth import get_login_limiter
    from app.services.login_limiter import LoginLimiter

    # A new limiter each time, so one test's failed sign-ins cannot block another's.
    limiter = LoginLimiter()
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_login_limiter] = lambda: limiter
    return TestClient(app)


@pytest.fixture
def _restore_app():
    """Undo the changes _client makes to the app, after the test."""
    yield
    from app.main import app

    app.dependency_overrides.clear()


@pytest.fixture
def client_with_data(_restore_app):
    """Make a test client whose database holds the given trades and prices."""
    return lambda trades, prices=None: _client(FakeSession(trades, prices or []))


@pytest.fixture
def client_with_users(_restore_app):
    """Make a test client whose database holds the given users."""
    return lambda *users: _client(FakeSession(users=users))
