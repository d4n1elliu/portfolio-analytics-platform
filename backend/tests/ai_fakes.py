"""Fake AI models for the tests, so no test calls a real API."""

import hashlib

from langchain_core.embeddings import Embeddings
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

EMBEDDING_SIZE = 8
TOKENS_PER_ANSWER = {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15}


def scripted_chat_model(*answers: str) -> GenericFakeChatModel:
    messages = [AIMessage(content=answer, usage_metadata=TOKENS_PER_ANSWER) for answer in answers]
    return GenericFakeChatModel(messages=iter(messages))


class FakeEmbeddings(Embeddings):
    def embed_query(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode()).digest()
        return [byte / 255 for byte in digest[:EMBEDDING_SIZE]]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]
