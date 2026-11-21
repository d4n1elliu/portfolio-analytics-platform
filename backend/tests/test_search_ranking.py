"""Combining rankings, reranking, rewriting a follow-up and choosing the reranker. No database."""

from datetime import date

import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from ai_fakes import KeywordReranker, scripted_chat_model
from app.ai import providers
from app.ai.assistant import TokenCount
from app.ai.query_rewriting import MAX_QUERY_LENGTH, follow_up_rewriter
from app.ai.retrieval import RetrievedChunk, fuse, reranked

EARLIER = ["How is Commonwealth Bank doing?"]


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


def test_a_first_question_is_searched_as_asked_without_calling_the_model():
    rewrite = follow_up_rewriter(scripted_chat_model(), [], TokenCount())

    assert rewrite("Is its dividend safe?") == "Is its dividend safe?"


def test_a_follow_up_is_rewritten_and_its_tokens_are_counted():
    tokens_used = TokenCount()
    model = scripted_chat_model("Is the Commonwealth Bank\ndividend safe?")

    rewritten = follow_up_rewriter(model, EARLIER, tokens_used)("Is its dividend safe?")

    assert rewritten == "Is the Commonwealth Bank dividend safe?"
    assert (tokens_used.input_tokens, tokens_used.output_tokens) == (10, 5)


@pytest.mark.parametrize(
    "reply", ["", "   ", "x" * (MAX_QUERY_LENGTH + 1)], ids=["empty", "spaces", "too long"]
)
def test_a_rewrite_that_cannot_be_used_falls_back_to_the_query_as_asked(reply):
    rewrite = follow_up_rewriter(scripted_chat_model(reply), EARLIER, TokenCount())

    assert rewrite("Is its dividend safe?") == "Is its dividend safe?"


def test_a_model_failure_falls_back_to_the_query_as_asked():
    rewrite = follow_up_rewriter(FakeListChatModel(responses=[]), EARLIER, TokenCount())

    assert rewrite("Is its dividend safe?") == "Is its dividend safe?"


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
