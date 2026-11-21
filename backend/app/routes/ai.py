"""Endpoints for the AI features. They answer 404 while the AI features are off."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.ai.providers import embeddings_loader, get_chat_model
from app.ai.usage import Allowance
from app.database import get_db
from app.models import User
from app.routes.dependencies import (
    get_ai_allowance,
    get_current_user,
    require_ai_allowance,
    require_ai_enabled,
)
from app.schemas.ai import AiUsageRead, ChatRequest

if TYPE_CHECKING:
    from collections.abc import Callable

    from langchain_core.embeddings import Embeddings
    from langchain_core.language_models import BaseChatModel

router = APIRouter(prefix="/ai", tags=["ai"], dependencies=[Depends(require_ai_enabled)])

STREAM_HEADERS = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}


@router.get("/usage", response_model=AiUsageRead)
def read_ai_usage(allowance: Allowance = Depends(get_ai_allowance)):
    """Return how many AI requests and tokens the signed-in user has used, and their limits."""
    return allowance


@router.post("/chat", dependencies=[Depends(require_ai_allowance)])
def chat(
    request: ChatRequest,
    user: User = Depends(get_current_user),
    model: BaseChatModel = Depends(get_chat_model),
    load_embeddings: Callable[[], Embeddings] = Depends(embeddings_loader),
    db: Session = Depends(get_db),
):
    """Answer a question about the portfolio, streamed as server-sent events.

    Each event is a JSON object with a type: text, tool_call, tool_result, sources, done or
    error.
    """
    from app.ai import assistant

    turns = [assistant.ChatTurn(turn.role, turn.text) for turn in request.messages]
    models = assistant.Models(model, load_embeddings)
    events = assistant.answer_events(models, db, user, turns)
    return StreamingResponse(
        (_server_sent(event) for event in events),
        media_type="text/event-stream",
        headers=STREAM_HEADERS,
    )


def _server_sent(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"
