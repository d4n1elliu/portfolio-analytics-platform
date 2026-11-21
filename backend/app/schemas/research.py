"""Response shapes for research documents."""

import datetime

from pydantic import BaseModel

from app.models import ResearchDocument


class ResearchChunkRead(BaseModel):
    id: int
    position: int
    text: str


class ResearchDocumentRead(BaseModel):
    id: int
    title: str
    file_name: str
    ticker: str
    document_date: datetime.date
    chunk_count: int
    uploaded_by: str
    created_at: datetime.datetime

    @classmethod
    def from_document(cls, document: ResearchDocument) -> "ResearchDocumentRead":
        return cls(**_summary(document))


class ResearchDocumentDetailRead(ResearchDocumentRead):
    chunks: list[ResearchChunkRead]

    @classmethod
    def from_document(cls, document: ResearchDocument) -> "ResearchDocumentDetailRead":
        chunks = [
            ResearchChunkRead(id=chunk.id, position=chunk.position, text=chunk.text)
            for chunk in document.chunks
        ]
        return cls(**_summary(document), chunks=chunks)


def _summary(document: ResearchDocument) -> dict:
    return {
        "id": document.id,
        "title": document.title,
        "file_name": document.file_name,
        "ticker": document.security.ticker,
        "document_date": document.document_date,
        "chunk_count": len(document.chunks),
        "uploaded_by": document.uploaded_by.name,
        "created_at": document.created_at,
    }
