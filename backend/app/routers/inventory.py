"""
Inventory router for MediStock.

STATUS: Phase 0 placeholder — router is NOT mounted in main.py yet.

Phase 1 endpoints (see docs/PROJECT_CONTEXT.md §8):
  GET  /api/facilities                   — list all facilities
  GET  /api/inventory/{facility_id}      — inventory for one facility with risk levels
  POST /api/inventory/{facility_id}/consume — record a consumption event
  GET  /api/risk                         — risk summary across all facilities
"""

from fastapi import APIRouter

router = APIRouter(prefix="/inventory", tags=["inventory"])

# Phase 1: implement endpoint handlers here.
