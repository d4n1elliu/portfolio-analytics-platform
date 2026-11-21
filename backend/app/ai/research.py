"""Stores research documents as embedded chunks, and reads them back."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models import ResearchChunk, ResearchDocument, Security, User
from app.models.research import FILE_NAME_LENGTH
from app.services.csv_parsing import ImportDuplicateError

if TYPE_CHECKING:
    from langchain_core.embeddings import Embeddings

PDF_TYPE = ".pdf"
FILE_TYPES = (PDF_TYPE, ".md", ".txt")
MAX_DOCUMENTS_LISTED = 500


@dataclass(frozen=True)
class ResearchUpload:
    file_name: str
    content: bytes
    title: str
    document_date: date


def add_document(
    db: Session, embeddings: Embeddings, upload: ResearchUpload, security: Security, user: User
) -> ResearchDocument:
    from app.ai.documents import extract_text, split_into_chunks

    file_hash = hashlib.sha256(upload.content).hexdigest()
    earlier = db.scalar(select(ResearchDocument).where(ResearchDocument.file_hash == file_hash))
    if earlier is not None:
        raise ImportDuplicateError(
            f"This file was already uploaded as '{earlier.title}'. Nothing was saved."
        )

    chunks = split_into_chunks(extract_text(upload.file_name, upload.content))
    vectors = embeddings.embed_documents(chunks)
    document = ResearchDocument(
        security=security,
        uploaded_by=user,
        title=upload.title.strip(),
        file_name=upload.file_name[:FILE_NAME_LENGTH],
        file_hash=file_hash,
        document_date=upload.document_date,
        chunks=[
            ResearchChunk(position=position, text=text, embedding=vector)
            for position, (text, vector) in enumerate(zip(chunks, vectors), start=1)
        ],
    )
    db.add(document)
    db.commit()
    return document


def list_documents(db: Session, security: Security | None = None) -> list[ResearchDocument]:
    statement = (
        _with_details(select(ResearchDocument))
        .order_by(ResearchDocument.document_date.desc(), ResearchDocument.id.desc())
        .limit(MAX_DOCUMENTS_LISTED)
    )
    if security is not None:
        statement = statement.where(ResearchDocument.security_id == security.id)
    return list(db.scalars(statement))


def find_document(db: Session, document_id: int) -> ResearchDocument | None:
    statement = _with_details(select(ResearchDocument)).where(ResearchDocument.id == document_id)
    return db.scalar(statement)


def _with_details(statement):
    return statement.options(
        joinedload(ResearchDocument.security),
        joinedload(ResearchDocument.uploaded_by),
        selectinload(ResearchDocument.chunks),
    )
