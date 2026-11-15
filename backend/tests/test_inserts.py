"""Inserting rows that may already exist. No database is used."""

from sqlalchemy.dialects import postgresql

from app.models import User
from app.services.inserts import insert_missing

ROW = {"email": "a@example.com", "name": "A", "role": "analyst", "password_hash": "hash"}


class RecordingSession:
    """Keeps the statement it is given and answers with the rows it was told to."""

    def __init__(self, inserted):
        self.inserted = inserted
        self.sql = ""

    def execute(self, statement):
        self.sql = str(statement.compile(dialect=postgresql.dialect()))
        return self

    def scalars(self):
        return self.inserted


def test_existing_rows_are_skipped_instead_of_failing():
    session = RecordingSession([])

    insert_missing(session, User, [ROW], ["email"], User.email)

    assert "ON CONFLICT (email) DO NOTHING" in session.sql


def test_only_the_inserted_rows_are_returned():
    session = RecordingSession(["a@example.com"])

    inserted = insert_missing(session, User, [ROW], ["email"], User.email)

    assert inserted == ["a@example.com"]
    assert "RETURNING users.email" in session.sql
