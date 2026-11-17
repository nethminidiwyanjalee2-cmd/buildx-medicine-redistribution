"""
Redistribution Recommendations API Router for MediStock.

Handles:
  - Triggering the multi-facility redistribution engine
  - Strategy comparisons (priority_greedy vs proportional_fairness)
  - Executing approved stock transfers between facilities
  - Resetting to deterministic seed data for live demonstrations
"""

from fastapi import APIRouter, HTTPException

from app.data import db
from app.engine.optimiser import recommend_redistribution
from app.models.recommendation import (
    OptimiserRunRequest,
    ExecuteTransferRequest,
)

router = APIRouter(prefix="", tags=["recommendations"])


@router.get("/recommendations")
def get_recommendations():
    """
    Retrieve latest redistribution recommendations.
    If no recommendations have been generated yet, automatically runs the optimiser.
    """
    saved = db.get_saved_recommendations()
    if not saved:
        # Generate initial batch
        items = db.get_inventory()
        recs = recommend_redistribution(items, strategy="priority_greedy")
        db.save_recommendations(recs)
        return recs
    return saved


@router.post("/recommendations/run")
def run_optimiser(payload: OptimiserRunRequest):
    """
    Execute the redistribution optimiser algorithm over the current inventory state.
    Matches deficit hospitals with excess donor hospitals based on the selected strategy.
    """
    items = db.get_inventory()
    recs = recommend_redistribution(
        inventory_snapshot=items,
        strategy=payload.strategy,
        min_transfer_units=payload.min_transfer_units,
    )
    db.save_recommendations(recs)

    total_units = sum(r["quantity"] for r in recs)
    urgent_count = sum(1 for r in recs if r["urgency"] == "HIGH")

    return {
        "status": "success",
        "strategy": payload.strategy,
        "recommendation_count": len(recs),
        "urgent_count": urgent_count,
        "total_units_to_redistribute": total_units,
        "recommendations": recs,
    }


@router.post("/recommendations/execute")
def execute_recommendation_transfer(payload: ExecuteTransferRequest):
    """
    Applies an approved redistribution transfer:
    Decrements units from the donor hospital and increments units at the recipient hospital.
    """
    result = db.execute_transfer(payload.recommendation_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Execution failed"))
    return result


@router.post("/seed/reset")
def reset_seed_data():
    """
    Reset all facilities, inventory levels, and consumption logs to the original
    clean deterministic baseline. Extremely useful during judging evaluations.
    """
    return db.reset_to_seed_data()
