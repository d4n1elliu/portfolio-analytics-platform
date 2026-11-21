"""AiUsage model: the tokens one AI request used, and who made it."""

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.common import CreatedAtMixin


class AiUsage(CreatedAtMixin, Base):
    __tablename__ = "ai_usage"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    input_tokens: Mapped[int] = mapped_column(Integer)
    output_tokens: Mapped[int] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"<AiUsage of user {self.user_id}: {self.input_tokens + self.output_tokens} tokens>"
