"""
Redistribution optimiser for MediStock.

STATUS: Phase 0 placeholder — do NOT implement logic here yet.

Phase 2 specification (see docs/PROJECT_CONTEXT.md §7.3):
  Input:
    inventory_snapshot: list[dict]
      Each dict represents one (facility, medicine) combination and includes:
        facility_id, medicine_id, current_stock, days_to_depletion, risk_level

  Output:
    list[dict] — redistribution recommendations, each:
    {
      "from_facility": str,
      "to_facility": str,
      "medicine_id": str,
      "quantity": int,
      "urgency": "high" | "medium" | "low",
      "reason": str
    }

  Algorithm (priority-queue approach):
    1. Collect all "critical" and "warning" items as deficit sites.
    2. Collect all "excess" items as surplus sites.
    3. Sort deficit sites by days_to_depletion ascending (most urgent first).
    4. For each deficit, find surplus of same medicine_id and allocate
       min(surplus_available, deficit_required) units.
    5. Record reason string in plain language for dashboard display.

  This module MUST NOT import firebase_admin, fastapi, or any app.data module.
"""


def recommend_redistribution(inventory_snapshot: list) -> list:
    """
    Generate redistribution recommendations from an inventory snapshot.

    Not yet implemented — raises NotImplementedError in Phase 0.
    """
    raise NotImplementedError(
        "optimiser.recommend_redistribution() will be implemented in Phase 2."
    )
