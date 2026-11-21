"""Endpoints for the AI features. They answer 404 while the AI features are off."""

from fastapi import APIRouter, Depends

from app.ai.usage import Allowance
from app.routes.dependencies import get_ai_allowance, require_ai_enabled
from app.schemas.ai import AiUsageRead

router = APIRouter(prefix="/ai", tags=["ai"], dependencies=[Depends(require_ai_enabled)])


@router.get("/usage", response_model=AiUsageRead)
def read_ai_usage(allowance: Allowance = Depends(get_ai_allowance)):
    """Return how many AI requests and tokens the signed-in user has used, and their limits."""
    return allowance
