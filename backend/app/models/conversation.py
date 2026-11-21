"""Conversation model: one conversation a user has had with the assistant."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.common import CreatedAtMixin

TITLE_LENGTH = 80


class Conversation(CreatedAtMixin, Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(TITLE_LENGTH))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<Conversation {self.id} of user {self.user_id}>"
