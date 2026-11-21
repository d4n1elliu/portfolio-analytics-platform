"""Request and response shapes for the AI features."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

MAX_QUESTION_LENGTH = 4000


class AiUsageRead(BaseModel):
    requests_used: int
    requests_limit: int
    tokens_used: int
    tokens_limit: int


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=MAX_QUESTION_LENGTH)
    conversation_id: str | None = Field(None, max_length=36)


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    updated_at: datetime


class ConversationDetailRead(ConversationRead):
    turns: list[dict]
