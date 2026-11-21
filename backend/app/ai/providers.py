"""Builds the models named in the settings, importing the AI packages only when first needed."""

from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING

from app.config import AI_CHAT_MODEL, AI_EMBEDDING_MODEL

LOCAL_MODEL_PREFIX = "fastembed:"

if TYPE_CHECKING:
    from collections.abc import Callable

    from langchain_core.embeddings import Embeddings
    from langchain_core.language_models import BaseChatModel


@cache
def get_chat_model() -> BaseChatModel:
    from langchain.chat_models import init_chat_model

    return init_chat_model(AI_CHAT_MODEL)


@cache
def get_embeddings() -> Embeddings:
    if AI_EMBEDDING_MODEL.startswith(LOCAL_MODEL_PREFIX):
        from app.ai.local_embeddings import LocalEmbeddings

        return LocalEmbeddings(AI_EMBEDDING_MODEL.removeprefix(LOCAL_MODEL_PREFIX))

    from langchain.embeddings import init_embeddings

    return init_embeddings(AI_EMBEDDING_MODEL)


def embeddings_loader() -> Callable[[], Embeddings]:
    return get_embeddings
