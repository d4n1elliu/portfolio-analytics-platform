"""Research models: an uploaded document, and the embedded chunks its text was split into."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import Date, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import CreatedAtMixin

if TYPE_CHECKING:
    from app.models.security import Security
    from app.models.user import User

FILE_NAME_LENGTH = 255
TITLE_LENGTH = 200
EMBEDDING_DIMENSIONS = 384


class ResearchDocument(CreatedAtMixin, Base):
    __tablename__ = "research_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    security_id: Mapped[int] = mapped_column(ForeignKey("securities.id"), index=True)
    uploaded_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(TITLE_LENGTH))
    file_name: Mapped[str] = mapped_column(String(FILE_NAME_LENGTH))
    file_hash: Mapped[str] = mapped_column(String(64), unique=True)
    document_date: Mapped[date] = mapped_column(Date, index=True)

    security: Mapped[Security] = relationship()
    uploaded_by: Mapped[User] = relationship()
    chunks: Mapped[list[ResearchChunk]] = relationship(
        back_populates="document", order_by="ResearchChunk.position", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ResearchDocument {self.title}>"


class ResearchChunk(Base):
    __tablename__ = "research_chunks"
    __table_args__ = (
        UniqueConstraint("document_id", "position", name="uq_research_chunks_document_id_position"),
        Index(
            "ix_research_chunks_embedding",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("research_documents.id"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIMENSIONS))

    document: Mapped[ResearchDocument] = relationship(back_populates="chunks")

    def __repr__(self) -> str:
        return f"<ResearchChunk {self.position} of document {self.document_id}>"
