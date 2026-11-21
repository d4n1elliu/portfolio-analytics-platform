"""Request and response shapes for the AI features."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator

MAX_TURNS = 40
MAX_TURN_LENGTH = 4000


class AiUsageRead(BaseModel):
    requests_used: int
    requests_limit: int
    tokens_used: int
    tokens_limit: int


class ChatTurnRequest(BaseModel):
    role: Literal["user", "assistant"]
    text: str = Field(min_length=1, max_length=MAX_TURN_LENGTH)


class ChatRequest(BaseModel):
    messages: list[ChatTurnRequest] = Field(min_length=1, max_length=MAX_TURNS)

    @model_validator(mode="after")
    def ends_with_a_question(self) -> "ChatRequest":
        if self.messages[-1].role != "user":
            raise ValueError("The last message must be from the user.")
        return self
