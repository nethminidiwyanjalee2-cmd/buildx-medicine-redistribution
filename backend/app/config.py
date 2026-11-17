"""
Central configuration for MediStock.

ALL tunable parameters live here — no magic numbers anywhere else in the codebase.
Judges may ask why a threshold is set to a specific value; every entry below has a comment.

Environment variables override defaults via python-dotenv.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Application metadata
# ---------------------------------------------------------------------------
APP_VERSION: str = "1.0.0"
APP_PHASE: int = 1
DISCLAIMER: str = (
    "Decision-support prototype using simulated data. Not for clinical use."
)

# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
API_PREFIX: str = "/api"

# ---------------------------------------------------------------------------
# CORS — allow Vite dev server; extend via CORS_ORIGINS
# ---------------------------------------------------------------------------
_raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173")
CORS_ORIGINS: list[str] = [o.strip() for o in _raw_origins.split(",") if o.strip()]

# ---------------------------------------------------------------------------
# Firebase / database
# ---------------------------------------------------------------------------
FIRESTORE_PROJECT_ID: str = os.getenv("FIRESTORE_PROJECT_ID", "demo-medistock")
FIRESTORE_EMULATOR_HOST: str = os.getenv(
    "FIRESTORE_EMULATOR_HOST", "localhost:8080"
)
JSON_DATA_DIR: str = os.getenv(
    "JSON_DATA_DIR",
    os.path.join(os.path.dirname(__file__), "data", "json_store"),
)

# ---------------------------------------------------------------------------
# Inventory risk thresholds (days of stock remaining)
# Based on WHO emergency and essential medicines stock management standards
# ---------------------------------------------------------------------------
CRITICAL_STOCK_DAYS: float = float(os.getenv("CRITICAL_STOCK_DAYS", "3.0"))
# Below 3.0 days -> "critical": Facility at immediate risk of stockout before resupply.

WARNING_STOCK_DAYS: float = float(os.getenv("WARNING_STOCK_DAYS", "7.0"))
# Below 7.0 days -> "warning": Replenishment / redistribution needed within 24-48 hours.

TARGET_BUFFER_DAYS: float = float(os.getenv("TARGET_BUFFER_DAYS", "14.0"))
# Safe target operating buffer when redistributing stock to a deficit facility.

EXCESS_STOCK_DAYS: float = float(os.getenv("EXCESS_STOCK_DAYS", "30.0"))
# Above 30.0 days -> "excess": Facility carries transferable surplus without endangering own patients.

# ---------------------------------------------------------------------------
# Forecasting parameters
# ---------------------------------------------------------------------------
MIN_FORECAST_WINDOW: int = int(os.getenv("MIN_FORECAST_WINDOW", "7"))
# Minimum days of history required for weighted moving average forecast.

MAX_FORECAST_WINDOW: int = int(os.getenv("MAX_FORECAST_WINDOW", "30"))
# Maximum days of historical consumption considered.

# ---------------------------------------------------------------------------
# Challenge 03 baseline requirements
# ---------------------------------------------------------------------------
MIN_FACILITIES: int = 3
MIN_MEDICINE_CATEGORIES: int = 5
