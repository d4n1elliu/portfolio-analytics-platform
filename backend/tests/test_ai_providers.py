"""Building the AI models, and the fakes the tests use in their place. No API is called."""

import pytest

from ai_fakes import TOKENS_PER_ANSWER
from app.ai import providers
from app.config import AI_CHAT_MODEL, AI_EMBEDDING_MODEL
from app.models.research import EMBEDDING_DIMENSIONS


def test_a_test_cannot_build_a_real_model():
    with pytest.raises(AssertionError, match="tried to build the real model"):
        providers.get_chat_model()
    with pytest.raises(AssertionError, match="tried to build the real model"):
        providers.get_embeddings()


def test_the_models_named_in_the_settings_are_built_once(monkeypatch):
    built = []
    monkeypatch.setattr(
        "langchain.chat_models.init_chat_model", lambda name: built.append(name) or "chat"
    )
    monkeypatch.setattr("fastembed.TextEmbedding", lambda name: built.append(name) or "local")

    assert providers.get_chat_model() == providers.get_chat_model() == "chat"
    assert providers.get_embeddings() is providers.get_embeddings()
    assert built == [AI_CHAT_MODEL, "BAAI/bge-small-en-v1.5"]


def test_an_embedding_model_from_a_provider_is_built_by_langchain(monkeypatch):
    monkeypatch.setattr(providers, "AI_EMBEDDING_MODEL", "openai:text-embedding-3-small")
    monkeypatch.setattr("langchain.embeddings.init_embeddings", lambda name: f"built {name}")

    assert providers.get_embeddings() == "built openai:text-embedding-3-small"


def test_the_settings_name_a_provider_and_a_model():
    assert AI_CHAT_MODEL == "anthropic:claude-opus-5-5"
    assert AI_EMBEDDING_MODEL == "fastembed:BAAI/bge-small-en-v1.5"


def test_the_fake_chat_model_gives_its_answers_in_order_with_token_counts(fake_chat_model):
    model = fake_chat_model("first", "second")

    first, second = model.invoke("a question"), model.invoke("another")

    assert [first.content, second.content] == ["first", "second"]
    assert first.usage_metadata == TOKENS_PER_ANSWER


def test_the_fake_embeddings_are_the_same_for_the_same_text(fake_embeddings):
    same, again, other = fake_embeddings.embed_documents(["BHP", "BHP", "CBA"])

    assert same == again != other
    assert len(fake_embeddings.embed_query("BHP")) == EMBEDDING_DIMENSIONS
