"""Endpoints for the AI features. They answer 404 while the AI features are off."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.ai import conversations
from app.ai.memory import get_checkpointer
from app.ai.providers import embeddings_loader, get_chat_model, reranker_loader
from app.ai.usage import Allowance
from app.database import get_db
from app.models import Conversation, User
from app.routes.dependencies import (
    get_ai_allowance,
    get_current_user,
    require_ai_allowance,
    require_ai_enabled,
)
from app.schemas.ai import AiUsageRead, ChatRequest, ConversationDetailRead, ConversationRead

if TYPE_CHECKING:
    from collections.abc import Callable

    from langchain_core.embeddings import Embeddings
    from langchain_core.language_models import BaseChatModel
    from langgraph.checkpoint.base import BaseCheckpointSaver

    from app.ai.retrieval import Reranker

router = APIRouter(prefix="/ai", tags=["ai"], dependencies=[Depends(require_ai_enabled)])

STREAM_HEADERS = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}


def get_conversation(
    conversation_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Conversation:
    conversation = conversations.find_conversation(db, user, conversation_id)
    if conversation is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "You have no conversation with this id.")
    return conversation


@router.get("/usage", response_model=AiUsageRead)
def read_ai_usage(allowance: Allowance = Depends(get_ai_allowance)):
    """Return how many AI requests and tokens the signed-in user has used, and their limits."""
    return allowance


@router.get("/conversations", response_model=list[ConversationRead])
def list_conversations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List the signed-in user's conversations with the assistant, most recently used first."""
    return conversations.list_conversations(db, user)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailRead)
def read_conversation(
    conversation: Conversation = Depends(get_conversation),
    memory: BaseCheckpointSaver = Depends(get_checkpointer),
):
    """Return one conversation: each question, and the events of each answer."""
    from app.ai.assistant import conversation_turns

    return ConversationDetailRead(
        id=conversation.id,
        title=conversation.title,
        updated_at=conversation.updated_at,
        turns=conversation_turns(memory, conversation.id),
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation: Conversation = Depends(get_conversation),
    memory: BaseCheckpointSaver = Depends(get_checkpointer),
    db: Session = Depends(get_db),
):
    """Delete one conversation and everything stored for it."""
    conversations.delete_conversation(db, memory, conversation)


@router.post("/chat", dependencies=[Depends(require_ai_allowance)])
def chat(
    request: ChatRequest,
    user: User = Depends(get_current_user),
    chat_model: BaseChatModel = Depends(get_chat_model),
    load_embeddings: Callable[[], Embeddings] = Depends(embeddings_loader),
    load_reranker: Callable[[], Reranker | None] = Depends(reranker_loader),
    memory: BaseCheckpointSaver = Depends(get_checkpointer),
    db: Session = Depends(get_db),
):
    """Ask the assistant a question, streamed as server-sent events.

    Give conversation_id to carry on a conversation. Without it, a new one is started. Each
    event is a JSON object with a type: conversation, text, tool_call, tool_result, sources,
    done or error.
    """
    from app.ai import assistant

    if request.conversation_id is None:
        conversation = conversations.start_conversation(db, user, request.question)
    else:
        conversation = get_conversation(request.conversation_id, user, db)
    events = assistant.answer_events(
        assistant.Assistant(chat_model, load_embeddings, memory, load_reranker),
        db,
        user,
        conversation,
        request.question,
    )
    return StreamingResponse(
        (_server_sent(event) for event in events),
        media_type="text/event-stream",
        headers=STREAM_HEADERS,
    )


def _server_sent(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"
