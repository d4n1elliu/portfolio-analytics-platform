"""FastAPI application entry point.

Run from the backend/ directory with:
    uvicorn app.main:app --reload
"""

import logging

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db

logger = logging.getLogger(__name__)

app = FastAPI(title="Portfolio Analytics API")

# CORS: browsers block a web page from calling an API on a different address
# unless the API allows it. The frontend runs on port 5173 and this API on
# port 8000, so the frontend's address has to be listed here.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Confirm the API is running. Does not use the database."""
    return {"status": "ok"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)) -> dict[str, str]:
    """Confirm the API can reach the database by running a trivial query."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        # The full error message can contain the database host name, so only
        # the error type is logged and the caller gets a generic message.
        logger.error("Database health check failed: %s", type(error).__name__)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unreachable",
        ) from None
    return {"status": "ok", "database": "connected"}
