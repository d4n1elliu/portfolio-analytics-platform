"""Reads the text of an uploaded research file and splits it into chunks. Uses no database."""

import io

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from pypdf.errors import PyPdfError

from app.ai.research import PDF_TYPE
from app.services.csv_parsing import ImportFileError

CHUNK_CHARACTERS = 1000
CHUNK_OVERLAP = 150
MAX_CHUNKS = 400


def extract_text(file_name: str, content: bytes) -> str:
    text = _pdf_text(content) if file_name.lower().endswith(PDF_TYPE) else _plain_text(content)
    text = text.replace("\x00", "").strip()
    if not text:
        raise ImportFileError("The file has no text that can be read.")
    return text


def split_into_chunks(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_CHARACTERS, chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_text(text)
    if len(chunks) > MAX_CHUNKS:
        raise ImportFileError(f"The file is too long. It would need more than {MAX_CHUNKS} chunks.")
    return chunks


def _plain_text(content: bytes) -> str:
    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ImportFileError("The file is not valid UTF-8 text.") from None


def _pdf_text(content: bytes) -> str:
    try:
        pages = PdfReader(io.BytesIO(content)).pages
        return "\n\n".join(page.extract_text() for page in pages)
    except PyPdfError:
        raise ImportFileError("The PDF could not be read.") from None
