"""An embedding model that runs on this machine, so embedding text costs nothing."""

import fastembed
from langchain_core.embeddings import Embeddings


class LocalEmbeddings(Embeddings):
    def __init__(self, model_name: str) -> None:
        self._model = fastembed.TextEmbedding(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [vector.tolist() for vector in self._model.embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        return next(iter(self._model.query_embed(text))).tolist()
