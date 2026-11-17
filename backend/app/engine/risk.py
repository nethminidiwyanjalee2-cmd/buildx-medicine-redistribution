"""
Stock risk classifier for MediStock.

STATUS: Phase 0 placeholder — do NOT implement logic here yet.

Phase 1 specification (see docs/PROJECT_CONTEXT.md §7.2):
  Input:
    {
      "days_to_depletion": float,
      "current_stock": int,
      "reorder_level": int
    }

  Output:
    {
      "risk_level": "critical" | "warning" | "ok" | "excess",
      "reason": str   # human-readable explanation for the dashboard
    }

  Thresholds (all from config.py — no magic numbers here):
    days_to_depletion < config.CRITICAL_STOCK_DAYS  → "critical"
    days_to_depletion < config.WARNING_STOCK_DAYS   → "warning"
    days_to_depletion > config.EXCESS_STOCK_DAYS    → "excess"
    otherwise                                        → "ok"

  This module MUST NOT import firebase_admin, fastapi, or any app.data module.
"""


def classify_risk(inventory_item: dict) -> dict:
    """
    Classify the risk level of a single inventory item.

    Not yet implemented — raises NotImplementedError in Phase 0.
    """
    raise NotImplementedError("risk.classify_risk() will be implemented in Phase 1.")
