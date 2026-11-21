"""Load the sample research notes, as if the demo Operations account had uploaded them.

Run from the backend/ directory, after scripts.seed and scripts.seed_users:
    python -m scripts.seed_research

Safe to run more than once: a note that was already loaded is skipped.
"""

import re
import sys
from datetime import date
from pathlib import Path

from app.ai import research
from app.ai.providers import get_embeddings
from app.database import SessionLocal
from app.services import securities, users
from app.services.csv_parsing import ImportDuplicateError

NOTES_DIR = Path(__file__).resolve().parent.parent / "sample_data" / "research"
UPLOADER_EMAIL = "operations@example.com"


def read_note(path: Path) -> tuple[research.ResearchUpload, str]:
    content = path.read_bytes()
    text = content.decode("utf-8")
    title = _line_after(text, "# ")
    ticker = _line_after(text, "**Ticker:** ")
    document_date = date.fromisoformat(_line_after(text, "**Date:** "))
    return research.ResearchUpload(path.name, content, title, document_date), ticker


def _line_after(text: str, prefix: str) -> str:
    found = re.search(rf"^{re.escape(prefix)}(.+)$", text, re.MULTILINE)
    if found is None:
        raise ValueError(f"The note has no line starting with '{prefix}'.")
    return found.group(1).strip()


def main() -> int:
    with SessionLocal() as db:
        uploader = users.find_by_email(db, UPLOADER_EMAIL)
        if uploader is None:
            print(f"Nothing was loaded. Run scripts.seed_users first to create {UPLOADER_EMAIL}.")
            return 1

        embeddings = get_embeddings()
        for path in sorted(NOTES_DIR.glob("*.md")):
            upload, ticker = read_note(path)
            security = securities.find_by_ticker(db, ticker)
            if security is None:
                print(f"  skipped {path.name}: no security has the ticker {ticker}")
                continue
            try:
                document = research.add_document(db, embeddings, upload, security, uploader)
                print(f"  loaded {path.name}: {len(document.chunks)} chunks")
            except ImportDuplicateError:
                db.rollback()
                print(f"  skipped {path.name}: already loaded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
