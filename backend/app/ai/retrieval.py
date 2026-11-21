"""Finds the research chunks whose meaning is closest to a question."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ResearchChunk, ResearchDocument, Security

if TYPE_CHECKING:
    from langchain_core.embeddings import Embeddings

TOP_CHUNKS = 5


@dataclass(frozen=True)
class ResearchFilters:
    ticker: str | None = None
    date_from: date | None = None
    date_to: date | None = None


@dataclass(frozen=True)
class RetrievedChunk:
    document_id: int
    title: str
    ticker: str
    document_date: date
    position: int
    text: str


def search(
    db: Session,
    embeddings: Embeddings,
    question: str,
    filters: ResearchFilters = ResearchFilters(),
    limit: int = TOP_CHUNKS,
) -> list[RetrievedChunk]:
    question_vector = embeddings.embed_query(question)
    statement = (
        select(ResearchChunk, ResearchDocument, Security.ticker)
        .join(ResearchChunk.document)
        .join(ResearchDocument.security)
        .order_by(ResearchChunk.embedding.cosine_distance(question_vector), ResearchChunk.id)
        .limit(limit)
    )
    if filters.ticker is not None:
        statement = statement.where(Security.ticker == filters.ticker.strip().upper())
    if filters.date_from is not None:
        statement = statement.where(ResearchDocument.document_date >= filters.date_from)
    if filters.date_to is not None:
        statement = statement.where(ResearchDocument.document_date <= filters.date_to)
    return [
        RetrievedChunk(
            document_id=document.id,
            title=document.title,
            ticker=ticker,
            document_date=document.document_date,
            position=chunk.position,
            text=chunk.text,
        )
        for chunk, document, ticker in db.execute(statement)
    ]
