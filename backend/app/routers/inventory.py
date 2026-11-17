"""
Inventory and Facilities API Router for MediStock.

Handles:
  - Facilities listing
  - Inventory search & filtering
  - Consumption event recording
  - Demand spike simulation
  - Aggregate risk matrix calculation
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.data import db
from app.models.inventory import (
    InventoryItem,
    ConsumeRequest,
    DemandSpikeRequest,
)

router = APIRouter(prefix="", tags=["inventory"])


@router.get("/facilities")
def list_facilities():
    """Return all simulated healthcare facilities."""
    return db.get_facilities()


@router.get("/facilities/{facility_id}")
def get_facility(facility_id: str):
    """Retrieve details for a single facility."""
    fac = db.get_facility_by_id(facility_id)
    if not fac:
        raise HTTPException(status_code=404, detail=f"Facility '{facility_id}' not found")
    return fac


@router.get("/inventory")
def list_inventory(
    facility_id: Optional[str] = Query(None, description="Filter by facility ID (e.g. FAC-001)"),
    category: Optional[str] = Query(None, description="Filter by medicine category"),
    risk_level: Optional[str] = Query(None, description="Filter by risk (CRITICAL, WARNING, OK, EXCESS)"),
    search: Optional[str] = Query(None, description="Search term for medicine or facility name"),
):
    """
    Query inventory items across all or filtered healthcare facilities.
    """
    items = db.get_inventory(
        facility_id=facility_id,
        category=category,
        risk_level=risk_level,
    )
    if search:
        s = search.lower().strip()
        items = [
            it for it in items
            if s in it.get("medicine_name", "").lower()
            or s in it.get("facility_name", "").lower()
            or s in it.get("category", "").lower()
        ]
    return items


@router.get("/inventory/{facility_id}")
def get_facility_inventory(facility_id: str):
    """Get all inventory records for a specific facility."""
    fac = db.get_facility_by_id(facility_id)
    if not fac:
        raise HTTPException(status_code=404, detail=f"Facility '{facility_id}' not found")
    return db.get_inventory(facility_id=facility_id)


@router.get("/inventory/{facility_id}/{medicine_id}")
def get_single_inventory_item(facility_id: str, medicine_id: str):
    """Get a single (facility, medicine) inventory record."""
    item = db.get_inventory_item(facility_id, medicine_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    return item


@router.post("/inventory/{facility_id}/{medicine_id}/consume")
def record_consumption_event(
    facility_id: str,
    medicine_id: str,
    payload: ConsumeRequest,
):
    """
    Record a medication consumption event. Deducts from current_stock,
    recalculates days-to-depletion, and updates risk classification.
    """
    item = db.get_inventory_item(facility_id, medicine_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory record not found")

    result = db.record_consumption(
        facility_id=facility_id,
        medicine_id=medicine_id,
        units=payload.units,
        date_str=payload.date,
    )
    return result


@router.post("/inventory/{facility_id}/{medicine_id}/spike")
def simulate_demand_spike(
    facility_id: str,
    medicine_id: str,
    payload: DemandSpikeRequest,
):
    """
    Advanced extension: Simulate a sudden surge in patient demand
    (e.g., epidemic spike, emergency influx). Immediately increases consumption
    by the multiplier factor to demonstrate rapid risk escalation.
    """
    item = db.get_inventory_item(facility_id, medicine_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory record not found")

    avg_burn = item.get("avg_daily_consumption", 20.0)
    spike_units = round(avg_burn * (payload.multiplier - 1.0) * payload.duration_days, 0)
    spike_units = max(10.0, spike_units)

    result = db.record_consumption(
        facility_id=facility_id,
        medicine_id=medicine_id,
        units=spike_units,
    )
    return {
        "scenario": payload.scenario_name,
        "multiplier": payload.multiplier,
        "spike_units_consumed": spike_units,
        "updated_inventory": result["updated_inventory"],
    }


@router.get("/risk/summary")
def get_risk_summary():
    """
    Return high-level risk metrics across the entire healthcare network:
    Counts of critical, warning, ok, excess, and total deficit vs total surplus.
    """
    items = db.get_inventory()
    critical = [x for x in items if x.get("risk_level") == "CRITICAL"]
    warning = [x for x in items if x.get("risk_level") == "WARNING"]
    excess = [x for x in items if x.get("risk_level") == "EXCESS"]
    ok = [x for x in items if x.get("risk_level") == "OK"]

    total_deficit = sum(x.get("deficit_units", 0) for x in critical + warning)
    total_surplus = sum(x.get("surplus_units", 0) for x in excess)

    return {
        "total_monitored_items": len(items),
        "critical_count": len(critical),
        "warning_count": len(warning),
        "ok_count": len(ok),
        "excess_count": len(excess),
        "total_deficit_units": total_deficit,
        "total_transferable_surplus_units": total_surplus,
        "critical_items": [
            {
                "facility_id": x["facility_id"],
                "facility_name": x["facility_name"],
                "medicine_id": x["medicine_id"],
                "medicine_name": x["medicine_name"],
                "days_to_depletion": x["days_to_depletion"],
                "current_stock": x["current_stock"],
                "deficit_units": x["deficit_units"],
                "reason": x["reason"],
            }
            for x in critical
        ],
        "excess_items": [
            {
                "facility_id": x["facility_id"],
                "facility_name": x["facility_name"],
                "medicine_id": x["medicine_id"],
                "medicine_name": x["medicine_name"],
                "days_to_depletion": x["days_to_depletion"],
                "current_stock": x["current_stock"],
                "surplus_units": x["surplus_units"],
            }
            for x in excess
        ],
    }


@router.get("/consumption-history/{facility_id}/{medicine_id}")
def get_consumption_history(facility_id: str, medicine_id: str, limit: int = 30):
    """Retrieve historical daily consumption data points for analytics."""
    logs = db.get_consumption_logs(facility_id, medicine_id, limit=limit)
    item = db.get_inventory_item(facility_id, medicine_id)
    return {
        "facility_id": facility_id,
        "medicine_id": medicine_id,
        "medicine_name": item.get("medicine_name") if item else "Medicine",
        "facility_name": item.get("facility_name") if item else "Facility",
        "logs": logs,
    }
