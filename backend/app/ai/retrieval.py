"""Finds the research chunks that best answer a question, by its meaning and by its words."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Protocol

from sqlalchemy import Select, Text, cast, func, select
from sqlalchemy.orm import Session

from app.models import ResearchChunk, ResearchDocument, Security
from app.models.research import TEXT_SEARCH_LANGUAGE

if TYPE_CHECKING:
    from langchain_core.embeddings import Embeddings

TOP_CHUNKS = 5
CANDIDATES = 20
RANK_FUSION_CONSTANT = 60


class Reranker(Protocol):
    def scores(self, question: str, texts: list[str]) -> list[float]: ...


def no_reranker() -> None:
    return None


@dataclass(frozen=True)
class ResearchFilters:
    ticker: str | None = None
    date_from: date | None = None
    date_to: date | None = None


@dataclass(frozen=True)
class SearchOptions:
    match_words: bool = True
    reranker: Reranker | None = None


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
    options: SearchOptions = SearchOptions(),
) -> list[RetrievedChunk]:
    candidates = max(limit, CANDIDATES)
    rankings = [_closest_in_meaning(db, embeddings.embed_query(question), filters, candidates)]
    if options.match_words:
        rankings.append(_sharing_words(db, question, filters, candidates))
    chunks = _chunks(db, fuse(rankings))
    if options.reranker is not None:
        chunks = reranked(options.reranker, question, chunks)
    return chunks[:limit]


def fuse(rankings: list[list[int]]) -> list[int]:
    scores: dict[int, float] = defaultdict(float)
    for ranking in rankings:
        for rank, chunk_id in enumerate(ranking, start=1):
            scores[chunk_id] += 1 / (RANK_FUSION_CONSTANT + rank)
    return sorted(scores, key=lambda chunk_id: (-scores[chunk_id], chunk_id))


def reranked(
    reranker: Reranker, question: str, chunks: list[RetrievedChunk]
) -> list[RetrievedChunk]:
    scores = reranker.scores(question, [chunk.text for chunk in chunks])
    best_first = sorted(zip(scores, chunks), key=lambda scored: scored[0], reverse=True)
    return [chunk for _, chunk in best_first]


def _closest_in_meaning(
    db: Session, question_vector: list[float], filters: ResearchFilters, limit: int
) -> list[int]:
    distance = ResearchChunk.embedding.cosine_distance(question_vector)
    return list(db.scalars(_chunk_ids(filters).order_by(distance, ResearchChunk.id).limit(limit)))


def _sharing_words(db: Session, question: str, filters: ResearchFilters, limit: int) -> list[int]:
    every_word = cast(func.plainto_tsquery(TEXT_SEARCH_LANGUAGE, question), Text)
    any_word = func.to_tsquery(TEXT_SEARCH_LANGUAGE, func.replace(every_word, "&", "|"))
    statement = (
        _chunk_ids(filters)
        .where(ResearchChunk.search_vector.op("@@")(any_word))
        .order_by(func.ts_rank_cd(ResearchChunk.search_vector, any_word).desc(), ResearchChunk.id)
        .limit(limit)
    )
    return list(db.scalars(statement))


def _chunk_ids(filters: ResearchFilters) -> Select:
    statement = (
        select(ResearchChunk.id).join(ResearchChunk.document).join(ResearchDocument.security)
    )
    if filters.ticker is not None:
        statement = statement.where(Security.ticker == filters.ticker.strip().upper())
    if filters.date_from is not None:
        statement = statement.where(ResearchDocument.document_date >= filters.date_from)
    if filters.date_to is not None:
        statement = statement.where(ResearchDocument.document_date <= filters.date_to)
    return statement


def _chunks(db: Session, chunk_ids: list[int]) -> list[RetrievedChunk]:
    statement = (
        select(ResearchChunk, ResearchDocument, Security.ticker)
        .join(ResearchChunk.document)
        .join(ResearchDocument.security)
        .where(ResearchChunk.id.in_(chunk_ids))
    )
    found = {
        chunk.id: RetrievedChunk(
            document_id=document.id,
            title=document.title,
            ticker=ticker,
            document_date=document.document_date,
            position=chunk.position,
            text=chunk.text,
        )
        for chunk, document, ticker in db.execute(statement)
    }
    return [found[chunk_id] for chunk_id in chunk_ids]
