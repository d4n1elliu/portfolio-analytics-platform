"""Uploading research and reading it back, with PostgreSQL behind it and fake embeddings."""

from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import select

from ai_fakes import FakeEmbeddings
from app.ai.providers import get_embeddings
from app.main import app
from app.models import ResearchChunk, Role
from app.models.research import EMBEDDING_DIMENSIONS
from factories import make_pdf, make_security, make_user, sign_in
from scripts.seed_research import read_note

SAMPLE_NOTES = Path(__file__).resolve().parents[2] / "sample_data" / "research"
NOTE = b"# BHP\n\nIron ore shipments rose and unit costs stayed flat."
DETAILS = {"title": "BHP outlook", "ticker": "bhp", "document_date": "2026-10-12"}


@pytest.fixture
def signed_in(db, save, client_with_session, monkeypatch):
    monkeypatch.setattr("app.routes.dependencies.AI_ENABLED", True)
    app.dependency_overrides[get_embeddings] = FakeEmbeddings
    save(make_security("BHP"))

    def client_as(role: Role):
        save(make_user(role))
        client = client_with_session(db)
        sign_in(client, role)
        return client

    return client_as


def upload(client, file_name="bhp.md", content=NOTE, **changed):
    files = {"file": (file_name, content, "application/octet-stream")}
    return client.post("/research/documents", data={**DETAILS, **changed}, files=files)


def test_an_uploaded_note_is_split_embedded_and_listed(signed_in, db):
    client = signed_in(Role.ANALYST)

    response = upload(client)

    assert response.status_code == 201
    document = response.json()
    assert document["title"] == "BHP outlook"
    assert document["ticker"] == "BHP"
    assert document["document_date"] == "2026-10-12"
    assert document["chunk_count"] == 1
    assert document["uploaded_by"] == "Test analyst"
    assert client.get("/research/documents").json() == [document]
    chunk = db.scalars(select(ResearchChunk)).one()
    assert len(chunk.embedding) == EMBEDDING_DIMENSIONS


def test_a_document_is_read_with_its_chunks_in_order(signed_in):
    client = signed_in(Role.ANALYST)
    long_note = " ".join(f"Sentence {number} is about iron ore." for number in range(120))
    document_id = upload(client, content=long_note.encode()).json()["id"]

    document = client.get(f"/research/documents/{document_id}").json()

    positions = [chunk["position"] for chunk in document["chunks"]]
    assert positions == list(range(1, document["chunk_count"] + 1))
    assert len(positions) > 1
    assert document["chunks"][0]["text"].startswith("Sentence 0 is about iron ore.")


def test_a_pdf_is_read(signed_in):
    client = signed_in(Role.OPERATIONS)

    document_id = upload(client, "bhp.pdf", make_pdf("Copper output grew.")).json()["id"]

    chunks = client.get(f"/research/documents/{document_id}").json()["chunks"]
    assert [chunk["text"] for chunk in chunks] == ["Copper output grew."]


def test_the_same_file_cannot_be_uploaded_twice(signed_in):
    client = signed_in(Role.ANALYST)
    upload(client)

    response = upload(client, title="The same note again")

    assert response.status_code == 409
    assert response.json() == {
        "detail": "This file was already uploaded as 'BHP outlook'. Nothing was saved."
    }
    assert len(client.get("/research/documents").json()) == 1


def test_a_portfolio_manager_can_read_research_but_not_upload_it(signed_in):
    client = signed_in(Role.PORTFOLIO_MANAGER)

    assert upload(client).status_code == 403
    assert client.get("/research/documents").json() == []


@pytest.mark.parametrize(
    ("changed", "status", "detail"),
    [
        ({"ticker": "XYZ"}, 422, "No security has the ticker 'XYZ'."),
        (
            {"document_date": "2999-01-01"},
            422,
            "The date of the document cannot be in the future.",
        ),
        ({"file_name": "bhp.docx"}, 400, "The file must be a .pdf or .md or .txt file."),
        ({"content": b"  "}, 400, "The file has no text that can be read."),
    ],
    ids=["unknown ticker", "future date", "wrong file type", "no text"],
)
def test_an_upload_that_cannot_be_used_saves_nothing(signed_in, changed, status, detail):
    client = signed_in(Role.ANALYST)

    response = upload(client, **changed)

    assert response.status_code == status
    assert response.json() == {"detail": detail}
    assert client.get("/research/documents").json() == []


def test_a_document_that_does_not_exist_is_not_found(signed_in):
    response = signed_in(Role.ANALYST).get("/research/documents/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "No research document has this id."}


def test_every_sample_note_names_its_title_ticker_and_date():
    notes = [read_note(path) for path in sorted(SAMPLE_NOTES.glob("*.md"))]

    assert [ticker for _, ticker in notes] == ["BHP", "CBA", "CSL", "VAS", "WOW"]
    assert all(upload.title and upload.document_date <= date.today() for upload, _ in notes)
