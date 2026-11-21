"""Fake AI models for the tests, so no test calls a real API."""

import hashlib

from langchain_core.embeddings import Embeddings
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage

EMBEDDING_SIZE = 8
TOKENS_PER_ANSWER = {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15}


class ScriptedChatModel(FakeMessagesListChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


def scripted_chat_model(*answers: str | AIMessage) -> ScriptedChatModel:
    return ScriptedChatModel(responses=[_message(answer) for answer in answers])


def tool_call(name: str, **arguments) -> AIMessage:
    call = {"name": name, "args": arguments, "id": f"call_{name}"}
    return AIMessage(content="", tool_calls=[call], usage_metadata=TOKENS_PER_ANSWER)


def _message(answer: str | AIMessage) -> AIMessage:
    if isinstance(answer, AIMessage):
        return answer
    return AIMessage(content=answer, usage_metadata=TOKENS_PER_ANSWER)


class FakeEmbeddings(Embeddings):
    def embed_query(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode()).digest()
        return [byte / 255 for byte in digest[:EMBEDDING_SIZE]]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]
