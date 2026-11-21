"""Response shapes for the AI features."""

from pydantic import BaseModel


class AiUsageRead(BaseModel):
    requests_used: int
    requests_limit: int
    tokens_used: int
    tokens_limit: int
