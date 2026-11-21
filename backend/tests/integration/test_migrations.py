"""The migrations run against a real PostgreSQL database."""

from sqlalchemy import inspect

APP_TABLES = {"prices", "securities", "trades", "users"}


def test_models_match_the_migrations(migrated_engine, alembic):
    """Fails when a model was changed without adding a migration."""
    alembic("check")


def test_migrations_can_be_undone_and_applied_again(migrated_engine, alembic):
    alembic("downgrade", "base")
    assert not APP_TABLES & set(inspect(migrated_engine).get_table_names())

    alembic("upgrade", "head")
    assert APP_TABLES <= set(inspect(migrated_engine).get_table_names())
