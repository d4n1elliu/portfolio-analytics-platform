"""A reranking model that runs on this machine, so reordering search results costs nothing."""

from fastembed.rerank import cross_encoder


class LocalReranker:
    def __init__(self, model_name: str) -> None:
        self._model = cross_encoder.TextCrossEncoder(model_name)

    def scores(self, question: str, texts: list[str]) -> list[float]:
        return list(self._model.rerank(question, texts))
