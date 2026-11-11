"""FastAPI application entry point.

Run from the backend/ directory with:
    uvicorn app.main:app --reload
"""

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load variables from backend/.env (if present) into the process environment.
# Nothing reads them yet; this is in place for database and auth settings later.
load_dotenv()

app = FastAPI(title="Portfolio Analytics API")

# The Vite dev server runs on a different origin (port 5173) from the API
# (port 8000), so the browser blocks its requests unless the API allows it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check used by the frontend and, later, by deployment tooling."""
    return {"status": "ok"}
