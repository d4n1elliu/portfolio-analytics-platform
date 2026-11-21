"""Builds the chat model and the embedding model named in the settings."""

from functools import cache

from langchain.chat_models import init_chat_model
from langchain.embeddings import init_embeddings
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel

from app.config import AI_CHAT_MODEL, AI_EMBEDDING_MODEL


@cache
def get_chat_model() -> BaseChatModel:
    return init_chat_model(AI_CHAT_MODEL)


@cache
def get_embeddings() -> Embeddings:
    return init_embeddings(AI_EMBEDDING_MODEL)
