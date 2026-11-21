"""Test setup. pytest runs this file before it collects any tests."""

import os
from pathlib import Path

import pytest
from dotenv import dotenv_values

TEST_DATABASE_VARIABLE = "TEST_DATABASE_URL"


def _test_database_url() -> str:
    """Return TEST_DATABASE_URL from the shell or backend/.env, or "" when it is unset."""
    env_file = dotenv_values(Path(__file__).resolve().parent.parent / ".env")
    return (
        os.environ.get(TEST_DATABASE_VARIABLE) or env_file.get(TEST_DATABASE_VARIABLE) or ""
    ).strip()


os.environ[TEST_DATABASE_VARIABLE] = _test_database_url()
if os.environ[TEST_DATABASE_VARIABLE]:
    os.environ["DATABASE_URL"] = os.environ[TEST_DATABASE_VARIABLE]
elif not os.environ.get("DATABASE_URL", "").strip():
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"

# A made-up secret for signing tokens, so the tests never use a real one.
os.environ["JWT_SECRET"] = "test-secret-that-is-long-enough-for-hs256"

# Every optional setting is emptied, so the tests use the defaults whatever is
# in the developer's own .env file, and never hold a real API key.
OPTIONAL_SETTINGS = (
    "AI_ENABLED",
    "AI_CHAT_MODEL",
    "AI_EMBEDDING_MODEL",
    "AI_REQUESTS_PER_HOUR",
    "AI_DAILY_TOKEN_CAP",
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "BENCHMARK_TICKER",
    "CORS_ORIGINS",
    "DEFAULT_PAGE_SIZE",
    "IMPORT_MAX_FILE_BYTES",
    "IMPORT_MAX_ROWS",
    "MARKET_TIMEZONE",
    "MAX_PAGE_SIZE",
    "PASSWORD_LOCKED_EMAILS",
    "SESSION_MINUTES",
)
os.environ.update(dict.fromkeys(OPTIONAL_SETTINGS, ""))


class FakeSession:
    """Stands in for the database session. Returns the rows that match the query."""

    def __init__(self, trades=(), prices=(), users=()):
        self.trades = trades
        self.prices = prices
        self.users = users
        self.user_sessions = []

    def add(self, row):
        self.user_sessions.append(row)

    def commit(self):
        pass

    def scalars(self, statement):
        from app.models import Price

        asks_for_prices = statement.column_descriptions[0]["entity"] is Price
        return self.prices if asks_for_prices else self.trades

    def execute(self, statement):
        """Accept any statement, such as the health check's query."""

    def scalar(self, statement):
        """Return the user or session whose columns equal the values in the query, such as an email.

        Any other query, such as a count, gets None.
        """
        from app.models import User, UserSession

        rows = {User: self.users, UserSession: self.user_sessions}.get(
            statement.column_descriptions[0]["entity"]
        )
        if rows is None:
            return None
        wanted = {
            name.rsplit("_", 1)[0]: value for name, value in statement.compile().params.items()
        }
        for row in rows:
            if all(getattr(row, column) == value for column, value in wanted.items()):
                return row
        return None


def _client(session: FakeSession, signed_in_as=None):
    """Make a test client that uses the given session instead of a database.

    Give a user to skip signing in: every request is then made as that user.
    """
    # Imported here because the app needs DATABASE_URL, which is set above.
    from fastapi.testclient import TestClient

    from app.database import get_db
    from app.main import app
    from app.routes.auth import get_login_limiter
    from app.routes.dependencies import get_current_user
    from app.services.login_limiter import LoginLimiter

    # A new limiter each time, so one test's failed sign-ins cannot block another's.
    limiter = LoginLimiter()
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_login_limiter] = lambda: limiter
    if signed_in_as is not None:
        app.dependency_overrides[get_current_user] = lambda: signed_in_as
    return TestClient(app)


@pytest.fixture(autouse=True)
def no_real_ai_models(monkeypatch):
    from app.ai import providers

    def refuse(name, *args, **kwargs):
        raise AssertionError(f"A test tried to build the real model {name}. Use a fake one.")

    monkeypatch.setattr(providers, "init_chat_model", refuse)
    monkeypatch.setattr(providers, "init_embeddings", refuse)
    providers.get_chat_model.cache_clear()
    providers.get_embeddings.cache_clear()


@pytest.fixture
def fake_chat_model():
    from ai_fakes import scripted_chat_model

    return scripted_chat_model


@pytest.fixture
def fake_embeddings():
    from ai_fakes import FakeEmbeddings

    return FakeEmbeddings()


@pytest.fixture
def _restore_app():
    """Undo the changes _client makes to the app, after the test."""
    yield
    from app.main import app

    app.dependency_overrides.clear()


@pytest.fixture
def client_with_session(_restore_app):
    """Make a test client that uses the given session, such as one on a real database."""
    return _client


@pytest.fixture
def client_with_data(_restore_app):
    """Make a test client, signed in, whose database holds the given trades and prices."""
    from app.models import Role
    from factories import make_user

    return lambda trades, prices=None: _client(
        FakeSession(trades, prices or []), signed_in_as=make_user(Role.OPERATIONS)
    )


@pytest.fixture
def client_with_users(_restore_app):
    """Make a test client whose database holds the given users."""
    return lambda *users: _client(FakeSession(users=users))
