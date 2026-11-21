"""Reading the text of a research file and splitting it into chunks. No database is used."""

import pytest

from app.ai.documents import (
    CHUNK_CHARACTERS,
    CHUNK_OVERLAP,
    MAX_CHUNKS,
    extract_text,
    split_into_chunks,
)
from app.services.csv_parsing import ImportFileError
from factories import make_pdf


def test_text_and_markdown_files_are_read_as_they_are():
    assert extract_text("note.txt", b"Iron ore prices rose.\n") == "Iron ore prices rose."
    assert extract_text("NOTE.MD", "﻿# BHP\n\nCopper grew.".encode()) == "# BHP\n\nCopper grew."


def test_the_text_of_a_pdf_is_read():
    assert extract_text("note.pdf", make_pdf("Iron ore prices rose.")) == "Iron ore prices rose."


@pytest.mark.parametrize(
    ("file_name", "content", "problem"),
    [
        ("note.txt", b"   \n", "The file has no text that can be read."),
        ("note.txt", b"\xff\xfe\x00", "The file is not valid UTF-8 text."),
        ("note.pdf", b"not a pdf", "The PDF could not be read."),
    ],
    ids=["no text", "not text", "not a PDF"],
)
def test_a_file_that_cannot_be_read_is_refused(file_name, content, problem):
    with pytest.raises(ImportFileError, match=problem):
        extract_text(file_name, content)


def test_text_that_postgres_cannot_store_is_left_out():
    assert extract_text("note.txt", b"Iron\x00 ore") == "Iron ore"


def test_a_short_text_is_one_chunk():
    assert split_into_chunks("Iron ore prices rose.") == ["Iron ore prices rose."]


def test_a_long_text_is_split_into_chunks_that_overlap():
    sentences = [f"Sentence number {number} is about iron ore." for number in range(100)]

    chunks = split_into_chunks(" ".join(sentences))

    assert len(chunks) > 1
    assert all(len(chunk) <= CHUNK_CHARACTERS for chunk in chunks)
    assert chunks[0][-CHUNK_OVERLAP // 2 :] in chunks[1]


def test_a_text_that_needs_too_many_chunks_is_refused():
    too_long = "word " * (CHUNK_CHARACTERS * (MAX_CHUNKS + 1) // 5)

    with pytest.raises(ImportFileError, match="The file is too long"):
        split_into_chunks(too_long)
