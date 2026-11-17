"""
MediStock FastAPI Application Entry Point.

BuildX 0.1 — Challenge 03: Intelligent Medicine Stock Monitoring and Redistribution.
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
from app.routers.inventory import router as inventory_router
from app.routers.recommendations import router as recommendations_router

app = FastAPI(
    title="MediStock API",
    description=(
        "Decision-support system for medicine stock monitoring, "
        "consumption forecasting, and multi-facility redistribution optimization. "
        "BuildX 0.1 — Challenge 03."
    ),
    version=APP_VERSION,
    docs_url=f"{API_PREFIX}/docs",
    redoc_url=f"{API_PREFIX}/redoc",
    openapi_url=f"{API_PREFIX}/openapi.json",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
app.include_router(inventory_router, prefix=API_PREFIX)
app.include_router(recommendations_router, prefix=API_PREFIX)


@app.get(f"{API_PREFIX}/health", tags=["meta"])
async def health() -> dict:
    """
    Liveness and configuration check.
    Returns version, active DB mode (Firestore vs JSON fallback), and mandatory disclaimer.
    """
    try:
        from app.data.db import DB_MODE
    except Exception:
        DB_MODE = "unavailable"

    return {
        "status": "ok",
        "version": APP_VERSION,
        "phase": APP_PHASE,
        "db_mode": DB_MODE,
        "disclaimer": DISCLAIMER,
    }
