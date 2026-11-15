"""The users table. No database is used."""

from pathlib import Path

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from app.models import Role, User

MIGRATIONS = Path(__file__).resolve().parent.parent / "alembic" / "versions"


def _users_table_sql() -> str:
    return str(CreateTable(User.__table__).compile(dialect=postgresql.dialect()))


def test_table_accepts_every_role():
    sql = _users_table_sql()

    for role in Role:
        assert f"'{role.value}'" in sql


def test_migration_accepts_every_role():
    migration = next(MIGRATIONS.glob("*_create_users_table.py")).read_text()

    for role in Role:
        assert f"'{role.value}'" in migration


def test_email_must_be_lowercase_and_unique():
    assert "email = lower(email)" in _users_table_sql()
    assert User.__table__.c.email.unique


def test_new_user_is_active_by_default():
    assert User.__table__.c.is_active.server_default is not None
