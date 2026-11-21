"""Where LangGraph keeps the messages of each conversation: its own tables in PostgreSQL."""

from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING

from app.config import DATABASE_URL

if TYPE_CHECKING:
    from langgraph.checkpoint.base import BaseCheckpointSaver

CHECKPOINT_TABLES = frozenset(
    {"checkpoints", "checkpoint_blobs", "checkpoint_writes", "checkpoint_migrations"}
)
SQLALCHEMY_DRIVER = "+psycopg"
MAX_CONNECTIONS = 4


@cache
def get_checkpointer() -> BaseCheckpointSaver:
    from langgraph.checkpoint.postgres import PostgresSaver
    from psycopg.rows import dict_row
    from psycopg_pool import ConnectionPool

    pool = ConnectionPool(
        DATABASE_URL.replace(SQLALCHEMY_DRIVER, "", 1),
        min_size=1,
        max_size=MAX_CONNECTIONS,
        kwargs={"autocommit": True, "row_factory": dict_row, "prepare_threshold": None},
        check=ConnectionPool.check_connection,
        open=True,
    )
    return PostgresSaver(pool)


def create_checkpoint_tables() -> None:
    """Call this when the app starts, never in a request: it waits for open transactions to end."""
    get_checkpointer().setup()


def stored_messages(checkpointer: BaseCheckpointSaver, conversation_id: str) -> list:
    saved = checkpointer.get_tuple(thread(conversation_id))
    return saved.checkpoint["channel_values"].get("messages", []) if saved else []


def thread(conversation_id: str) -> dict:
    return {"configurable": {"thread_id": conversation_id}}
