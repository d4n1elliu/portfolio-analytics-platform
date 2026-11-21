"""Starts, lists, finds and deletes the conversations each user has with the assistant."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Conversation, User
from app.models.conversation import TITLE_LENGTH

if TYPE_CHECKING:
    from langgraph.checkpoint.base import BaseCheckpointSaver

MAX_CONVERSATIONS_LISTED = 50


def start_conversation(db: Session, user: User, first_question: str) -> Conversation:
    conversation = Conversation(id=str(uuid4()), user_id=user.id, title=title_from(first_question))
    db.add(conversation)
    db.commit()
    return conversation


def find_conversation(db: Session, user: User, conversation_id: str) -> Conversation | None:
    statement = select(Conversation).where(
        Conversation.id == conversation_id, Conversation.user_id == user.id
    )
    return db.scalar(statement)


def list_conversations(db: Session, user: User) -> list[Conversation]:
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .order_by(Conversation.updated_at.desc(), Conversation.id)
        .limit(MAX_CONVERSATIONS_LISTED)
    )
    return list(db.scalars(statement))


def mark_used(db: Session, conversation: Conversation, now: datetime) -> None:
    conversation.updated_at = now
    db.commit()


def delete_conversation(
    db: Session, checkpointer: BaseCheckpointSaver, conversation: Conversation
) -> None:
    checkpointer.delete_thread(conversation.id)
    db.delete(conversation)
    db.commit()


def title_from(question: str) -> str:
    one_line = " ".join(question.split())
    if len(one_line) <= TITLE_LENGTH:
        return one_line
    return one_line[: TITLE_LENGTH - 1].rstrip() + "…"
