"""
Redistribution recommendations router for MediStock.

STATUS: Phase 0 placeholder — router is NOT mounted in main.py yet.

Phase 2 endpoints (see docs/PROJECT_CONTEXT.md §8):
  GET  /api/recommendations        — latest recommendations from last optimiser run
  POST /api/recommendations/run    — trigger a fresh optimiser run and return results
"""

from fastapi import APIRouter

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

# Phase 2: implement endpoint handlers here.
