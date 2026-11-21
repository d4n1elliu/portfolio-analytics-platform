"""Endpoints for research documents. They answer 404 while the AI features are off."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.ai import research
from app.ai.providers import get_embeddings
from app.database import get_db
from app.models import User
from app.models.research import TITLE_LENGTH
from app.routes.dependencies import (
    UploadedFile,
    get_current_user,
    read_research_upload,
    require_ai_enabled,
    require_permission,
)
from app.routes.errors import IMPORT_ERROR_RESPONSES
from app.schemas.research import ResearchDocumentDetailRead, ResearchDocumentRead
from app.services import securities
from app.services.market_time import market_today
from app.services.permissions import Permission

if TYPE_CHECKING:
    from langchain_core.embeddings import Embeddings

router = APIRouter(
    prefix="/research", tags=["research"], dependencies=[Depends(require_ai_enabled)]
)


@router.get("/documents", response_model=list[ResearchDocumentRead])
def list_documents(db: Session = Depends(get_db)):
    """List the research documents, newest first."""
    return [ResearchDocumentRead.from_document(found) for found in research.list_documents(db)]


@router.get("/documents/{document_id}", response_model=ResearchDocumentDetailRead)
def read_document(document_id: int, db: Session = Depends(get_db)):
    """Return one research document with the chunks its text was split into."""
    document = research.find_document(db, document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No research document has this id.")
    return ResearchDocumentDetailRead.from_document(document)


@router.post(
    "/documents",
    response_model=ResearchDocumentRead,
    status_code=status.HTTP_201_CREATED,
    responses=IMPORT_ERROR_RESPONSES,
    dependencies=[Depends(require_permission(Permission.UPLOAD_RESEARCH))],
)
def upload_document(
    title: str = Form(min_length=1, max_length=TITLE_LENGTH),
    ticker: str = Form(),
    document_date: date = Form(),
    upload: UploadedFile = Depends(read_research_upload),
    user: User = Depends(get_current_user),
    embeddings: Embeddings = Depends(get_embeddings),
    db: Session = Depends(get_db),
):
    """Upload a PDF, Markdown or text file about one security. Its text is split and embedded.

    Needs the permission to upload research. A file that was uploaded before is refused.
    """
    security = securities.find_by_ticker(db, ticker)
    if security is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, f"No security has the ticker '{ticker}'."
        )
    if document_date > market_today():
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "The date of the document cannot be in the future.",
        )
    details = research.ResearchUpload(upload.file_name, upload.content, title, document_date)
    document = research.add_document(db, embeddings, details, security, user)
    return ResearchDocumentRead.from_document(document)
