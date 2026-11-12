"""Alembic runs this file every time an alembic command is used.

It tells Alembic two things: how to connect to the database (the URL from
app.config, which reads backend/.env) and which tables should exist
(Base.metadata from app.database).
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.config import DATABASE_URL
from app.database import CONNECT_TIMEOUT_SECONDS, Base

config = context.config

# Apply the logging settings from alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# "alembic revision --autogenerate" compares these tables with the real
# database to work out what a new migration should contain. A model only
# appears here if its file has been imported, so import new model files in
# this file (or somewhere this file imports).
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Print the migration SQL instead of running it (alembic upgrade head --sql)."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Connect to the database and run migrations against it."""
    # The URL is passed straight to create_engine rather than through
    # alembic.ini, because a % character in a password has a special meaning
    # in .ini files and would break the URL. NullPool opens one connection and
    # closes it when the command finishes, since no pool is needed here.
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
        connect_args={"connect_timeout": CONNECT_TIMEOUT_SECONDS},
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
