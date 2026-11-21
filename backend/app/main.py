"""FastAPI application entry point.

Run from the backend/ directory with:
    uvicorn app.main:app --reload
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import AI_ENABLED, AI_TRACING, CORS_ORIGINS
from app.database import get_db
from app.request_log import LOG_FORMAT, log_request
from app.routes import ai, auth, holdings, portfolio, research, securities, trades
from app.routes.dependencies import get_current_user
from app.routes.errors import register_error_handlers

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def prepare_ai(app: FastAPI) -> AsyncIterator[None]:
    if AI_ENABLED:
        from app.ai.memory import create_checkpoint_tables

        try:
            create_checkpoint_tables()
        except Exception:
            logger.exception("Could not prepare the tables that hold conversations")
        if AI_TRACING:
            logger.info("Tracing is on: each answer's model and tool calls are sent to LangSmith")
    yield


app = FastAPI(title="Portfolio Analytics API", lifespan=prepare_ai)

# CORS: browsers block a web page from calling an API on a different address
# unless the API lists that address as allowed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Lets the page read how long a locked-out visitor must wait.
    expose_headers=["Retry-After"],
)

# Requests that only read data. A browser sends them from any site.
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


@app.middleware("http")
async def reject_cross_site_changes(request: Request, call_next):
    """Refuse a request that changes data if it comes from a site that is not allowed.

    A browser names the site a request came from in the Origin header. This
    stops another site from using a visitor's session. A request with no
    Origin is not from a browser page, so it has no session to misuse.
    """
    origin = request.headers.get("origin")
    if request.method not in SAFE_METHODS and origin and origin not in CORS_ORIGINS:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "This request came from a site that is not allowed."},
        )
    return await call_next(request)


app.middleware("http")(log_request)

register_error_handlers(app)

# Each router holds the endpoints for one area of the API.
app.include_router(auth.router)
# Every endpoint in these routers needs a signed-in user.
for router in (
    ai.router,
    holdings.router,
    portfolio.router,
    research.router,
    securities.router,
    trades.router,
):
    app.include_router(router, dependencies=[Depends(get_current_user)])


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
