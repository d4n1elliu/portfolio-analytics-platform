"""Database connection setup shared by the whole backend.

engine        manages the connections to PostgreSQL
SessionLocal  creates sessions, which are what the code uses to run queries
Base          the class every database model will inherit from
get_db        gives an endpoint a session for the length of one request
"""

from collections.abc import Iterator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import DATABASE_URL

CONNECT_TIMEOUT_SECONDS = 5

# The engine keeps a pool of open connections so each request can reuse one
# instead of opening its own. Creating the engine does not connect to the
# database; that happens on the first query.
engine = create_engine(
    DATABASE_URL,
    # Neon pauses a database that has been idle, which closes its connections.
    # This tests a connection before reusing it and replaces it if it is dead.
    pool_pre_ping=True,
    # Stop waiting after this many seconds if the database cannot be reached,
    # instead of leaving the request hanging.
    connect_args={"connect_timeout": CONNECT_TIMEOUT_SECONDS},
)

# autoflush=False: changes are sent to the database only on flush() or commit().
# expire_on_commit=False: objects can still be read after commit() without
# triggering another query.
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

# Name patterns for indexes (ix), unique constraints (uq), check constraints
# (ck), foreign keys (fk) and primary keys (pk). Without these the database
# invents the names, and a later migration cannot reliably refer to a
# constraint in order to change or remove it.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Parent class for every database model.

    Each model that inherits from Base is recorded in Base.metadata, which is
    how Alembic knows which tables should exist.
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def get_db() -> Iterator[Session]:
    """Give an endpoint a database session for one request.

    Use it as a parameter: db: Session = Depends(get_db). The session is
    closed when the request ends, even if the endpoint raised an error, which
    returns its connection to the pool.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
