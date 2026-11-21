"""Combining rankings, reranking and choosing the reranker. No database is used."""

from datetime import date

import pytest

from ai_fakes import KeywordReranker
from app.ai import providers
from app.ai.retrieval import RetrievedChunk, fuse, reranked


def chunk(text: str) -> RetrievedChunk:
    return RetrievedChunk(1, "A note", "BHP", date(2026, 10, 12), 1, text)


def test_a_chunk_found_by_both_searches_comes_first():
    assert fuse([[1, 2, 3], [3, 4]]) == [3, 1, 2, 4]


def test_one_ranking_keeps_its_order():
    assert fuse([[7, 5, 9]]) == [7, 5, 9]


def test_reranking_puts_the_highest_score_first_and_keeps_ties_in_order():
    chunks = [chunk("costs"), chunk("copper"), chunk("iron ore"), chunk("more copper")]

    best_first = reranked(KeywordReranker("copper"), "copper", chunks)

    assert [found.text for found in best_first] == ["copper", "more copper", "costs", "iron ore"]


def test_the_default_reranker_is_a_local_model(monkeypatch):
    built = []
    monkeypatch.setattr(
        "fastembed.rerank.cross_encoder.TextCrossEncoder", lambda name: built.append(name)
    )

    providers.get_reranker()

    assert built == ["Xenova/ms-marco-MiniLM-L-6-v2"]


def test_reranking_can_be_turned_off(monkeypatch):
    monkeypatch.setattr(providers, "AI_RERANK_MODEL", "off")

    assert providers.get_reranker() is None


def test_a_reranker_from_an_unknown_provider_is_refused(monkeypatch):
    monkeypatch.setattr(providers, "AI_RERANK_MODEL", "cohere:rerank")

    with pytest.raises(ValueError, match="AI_RERANK_MODEL must be 'off' or start with"):
        providers.get_reranker()
