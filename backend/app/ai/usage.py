"""Records each user's AI requests and tokens, and works out how much of their allowance is left."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import AI_DAILY_TOKEN_CAP, AI_REQUESTS_PER_HOUR
from app.models import AiUsage, User

REQUEST_WINDOW = timedelta(hours=1)
TOKEN_WINDOW = timedelta(days=1)


@dataclass(frozen=True)
class Allowance:
    requests_used: int
    requests_limit: int
    tokens_used: int
    tokens_limit: int

    @property
    def limit_reached(self) -> str | None:
        if self.requests_used >= self.requests_limit:
            return f"You have reached the limit of {self.requests_limit} AI requests an hour."
        if self.tokens_used >= self.tokens_limit:
            return f"You have reached the limit of {self.tokens_limit:,} AI tokens a day."
        return None


def read_allowance(db: Session, user: User, now: datetime) -> Allowance:
    return Allowance(
        requests_used=_requests_since(db, user, now - REQUEST_WINDOW),
        requests_limit=AI_REQUESTS_PER_HOUR,
        tokens_used=_tokens_since(db, user, now - TOKEN_WINDOW),
        tokens_limit=AI_DAILY_TOKEN_CAP,
    )


def record_usage(
    db: Session, user: User, input_tokens: int, output_tokens: int, now: datetime
) -> None:
    db.add(
        AiUsage(
            user_id=user.id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            created_at=now,
        )
    )
    db.commit()


def _requests_since(db: Session, user: User, start: datetime) -> int:
    statement = select(func.count()).select_from(AiUsage).where(_used_by(user, start))
    return db.scalar(statement) or 0


def _tokens_since(db: Session, user: User, start: datetime) -> int:
    tokens = func.sum(AiUsage.input_tokens + AiUsage.output_tokens)
    return db.scalar(select(tokens).where(_used_by(user, start))) or 0


def _used_by(user: User, start: datetime):
    return (AiUsage.user_id == user.id) & (AiUsage.created_at > start)
