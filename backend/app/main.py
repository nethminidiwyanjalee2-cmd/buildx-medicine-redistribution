"""
MediStock FastAPI application entry point.

Phase 0 deliverables:
  - CORS middleware configured from config.py
  - GET /api/health  → liveness check with db_mode and disclaimer
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import (
    API_PREFIX,
    APP_VERSION,
    APP_PHASE,
    CORS_ORIGINS,
    DISCLAIMER,
)

# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="MediStock API",
    description=(
        "Decision-support prototype for medicine stock monitoring and redistribution. "
        "BuildX 0.1 — Challenge 03."
    ),
    version=APP_VERSION,
    docs_url=f"{API_PREFIX}/docs",
    redoc_url=f"{API_PREFIX}/redoc",
    openapi_url=f"{API_PREFIX}/openapi.json",
)

# ---------------------------------------------------------------------------
# CORS — Vite dev server on :5173; extend via CORS_ORIGINS env var
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Phase 0 routes
# ---------------------------------------------------------------------------

@app.get(f"{API_PREFIX}/health", tags=["meta"])
async def health() -> dict:
    """
    Liveness check.

    Returns application version, current build phase, active database mode,
    and the mandatory disclaimer string. The frontend reads this to confirm
    the backend is reachable and to surface the db_mode to the team during
    development.
    """
    # Import here (not at module level) so the import error is caught gracefully
    # and reported in db_mode rather than crashing the app.
    try:
        from app.data.db import DB_MODE  # noqa: PLC0415
    except Exception:
        DB_MODE = "unavailable"

    return {
        "status": "ok",
        "version": APP_VERSION,
        "phase": APP_PHASE,
        "db_mode": DB_MODE,
        "disclaimer": DISCLAIMER,
    }
