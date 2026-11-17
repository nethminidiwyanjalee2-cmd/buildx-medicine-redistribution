"""
Database abstraction layer for MediStock.

Supports dual-mode storage:
  1. Firestore Emulator / Cloud Firestore (if credentials/emulator reachable)
  2. Persistent JSON Store fallback in app/data/json_store/ (default, zero-setup)

Exposes high-level repository methods for facilities, inventory, consumption logs,
and redistribution recommendations.
"""

import json
import os
import threading
from datetime import datetime
from typing import Any, Optional

from app.config import (
    JSON_DATA_DIR,
    FIRESTORE_PROJECT_ID,
    CRITICAL_STOCK_DAYS,
    WARNING_STOCK_DAYS,
    EXCESS_STOCK_DAYS,
    TARGET_BUFFER_DAYS,
)
from app.engine.forecaster import forecast
from app.engine.risk import classify_risk


# Global lock for thread-safe JSON file mutations
_store_lock = threading.Lock()

# Detect storage mode
DB_MODE = "json_fallback"
_firestore_db = None

try:
    import firebase_admin
    from firebase_admin import credentials, firestore

    # Only attempt if an emulator host or explicit creds are configured
    emulator_host = os.getenv("FIRESTORE_EMULATOR_HOST")
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if emulator_host or cred_path:
        if not firebase_admin._apps:
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {"projectId": FIRESTORE_PROJECT_ID})
            else:
                firebase_admin.initialize_app(options={"projectId": FIRESTORE_PROJECT_ID})
        _firestore_db = firestore.client()
        DB_MODE = "firestore"
except Exception:
    DB_MODE = "json_fallback"


# ---------------------------------------------------------------------------
# JSON Store Helpers
# ---------------------------------------------------------------------------

def _ensure_seed_data_loaded() -> None:
    """Ensure json_store directory and seed files exist; initialize if missing."""
    os.makedirs(JSON_DATA_DIR, exist_ok=True)
    inv_file = os.path.join(JSON_DATA_DIR, "inventory.json")
    if not os.path.exists(inv_file):
        from seed.seed_data import write_seed_files
        write_seed_files(JSON_DATA_DIR)


def _load_json_file(filename: str) -> list[dict[str, Any]]:
    """Read a JSON collection file."""
    _ensure_seed_data_loaded()
    path = os.path.join(JSON_DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []


def _save_json_file(filename: str, data: Any) -> None:
    """Safely write to a JSON collection file."""
    os.makedirs(JSON_DATA_DIR, exist_ok=True)
    path = os.path.join(JSON_DATA_DIR, filename)
    with _store_lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
# Facilities Repository
# ---------------------------------------------------------------------------

def get_facilities() -> list[dict[str, Any]]:
    """Return all simulated healthcare facilities."""
    return _load_json_file("facilities.json")


def get_facility_by_id(facility_id: str) -> Optional[dict[str, Any]]:
    """Return facility by its unique ID."""
    for fac in get_facilities():
        if fac.get("id") == facility_id:
            return fac
    return None


# ---------------------------------------------------------------------------
# Inventory Repository
# ---------------------------------------------------------------------------

def get_inventory(
    facility_id: Optional[str] = None,
    medicine_id: Optional[str] = None,
    risk_level: Optional[str] = None,
    category: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Query inventory with optional filters."""
    items = _load_json_file("inventory.json")

    filtered = items
    if facility_id:
        filtered = [x for x in filtered if x.get("facility_id") == facility_id]
    if medicine_id:
        filtered = [x for x in filtered if x.get("medicine_id") == medicine_id]
    if risk_level:
        filtered = [x for x in filtered if x.get("risk_level") == risk_level.upper()]
    if category:
        filtered = [x for x in filtered if x.get("category", "").lower() == category.lower()]

    return filtered


def get_inventory_item(facility_id: str, medicine_id: str) -> Optional[dict[str, Any]]:
    """Retrieve a single (facility, medicine) inventory record."""
    items = _load_json_file("inventory.json")
    for it in items:
        if it.get("facility_id") == facility_id and it.get("medicine_id") == medicine_id:
            return it
    return None


def update_inventory_item(facility_id: str, medicine_id: str, new_stock: float) -> Optional[dict[str, Any]]:
    """Update stock level, recalculate days-to-depletion and risk classification."""
    items = _load_json_file("inventory.json")
    target_idx = None

    for i, it in enumerate(items):
        if it.get("facility_id") == facility_id and it.get("medicine_id") == medicine_id:
            target_idx = i
            break

    if target_idx is None:
        return None

    item = items[target_idx]
    item["current_stock"] = max(0.0, float(new_stock))
    item["last_updated"] = datetime.now().isoformat()

    # Recalculate burn rate and risk
    logs = get_consumption_logs(facility_id, medicine_id)
    fc = forecast(logs, current_stock=item["current_stock"])
    burn = fc["avg_daily_consumption"]
    days_left = fc["days_to_depletion"]

    risk_info = classify_risk(
        inventory_item={
            "current_stock": item["current_stock"],
            "avg_daily_consumption": burn,
            "days_to_depletion": days_left,
            "reorder_level": item.get("reorder_level", 0.0),
            "medicine_name": item.get("medicine_name"),
            "facility_name": item.get("facility_name"),
        },
        critical_days=CRITICAL_STOCK_DAYS,
        warning_days=WARNING_STOCK_DAYS,
        excess_days=EXCESS_STOCK_DAYS,
        target_buffer_days=TARGET_BUFFER_DAYS,
    )

    item["avg_daily_consumption"] = burn
    item["days_to_depletion"] = risk_info["days_to_depletion"]
    item["risk_level"] = risk_info["risk_level"]
    item["deficit_units"] = risk_info["deficit_units"]
    item["surplus_units"] = risk_info["surplus_units"]
    item["reason"] = risk_info["reason"]
    item["trend"] = fc["trend"]

    items[target_idx] = item
    _save_json_file("inventory.json", items)
    return item


# ---------------------------------------------------------------------------
# Consumption Logs Repository
# ---------------------------------------------------------------------------

def get_consumption_logs(
    facility_id: str,
    medicine_id: str,
    limit: int = 30,
) -> list[dict[str, Any]]:
    """Return historical consumption logs for a specific facility & medicine."""
    all_logs = _load_json_file("consumption_logs.json")
    matched = [
        l for l in all_logs
        if l.get("facility_id") == facility_id and l.get("medicine_id") == medicine_id
    ]
    # Sort ascending by date
    matched.sort(key=lambda x: str(x.get("date", "")))
    return matched[-limit:] if len(matched) > limit else matched


def record_consumption(
    facility_id: str,
    medicine_id: str,
    units: float,
    date_str: Optional[str] = None,
) -> dict[str, Any]:
    """Record a consumption event, append to logs, and deduct from inventory."""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    all_logs = _load_json_file("consumption_logs.json")
    all_logs.append({
        "facility_id": facility_id,
        "medicine_id": medicine_id,
        "date": date_str,
        "units_consumed": float(units),
    })
    _save_json_file("consumption_logs.json", all_logs)

    # Deduct stock
    current_item = get_inventory_item(facility_id, medicine_id)
    if current_item:
        new_stock = max(0.0, float(current_item["current_stock"]) - float(units))
        updated_item = update_inventory_item(facility_id, medicine_id, new_stock)
        return {"log_entry": all_logs[-1], "updated_inventory": updated_item}

    return {"log_entry": all_logs[-1], "updated_inventory": None}


# ---------------------------------------------------------------------------
# Redistribution Recommendations Repository
# ---------------------------------------------------------------------------

def get_saved_recommendations() -> list[dict[str, Any]]:
    """Return persisted redistribution recommendations."""
    return _load_json_file("recommendations.json")


def save_recommendations(recs: list[dict[str, Any]]) -> None:
    """Save newly generated recommendations."""
    _save_json_file("recommendations.json", recs)


def execute_transfer(recommendation_id: str) -> dict[str, Any]:
    """
    Execute an approved redistribution transfer.
    Deducts stock from donor facility and credits stock to recipient facility.
    """
    recs = get_saved_recommendations()
    target_rec = None
    target_idx = None

    for i, r in enumerate(recs):
        if r.get("id") == recommendation_id:
            target_rec = r
            target_idx = i
            break

    if not target_rec:
        return {"success": False, "error": f"Recommendation {recommendation_id} not found"}

    if target_rec.get("status") == "EXECUTED":
        return {"success": False, "error": f"Recommendation {recommendation_id} was already executed"}

    from_fac = target_rec["from_facility_id"]
    to_fac = target_rec["to_facility_id"]
    med_id = target_rec["medicine_id"]
    qty = target_rec["quantity"]

    donor_item = get_inventory_item(from_fac, med_id)
    recip_item = get_inventory_item(to_fac, med_id)

    if not donor_item or not recip_item:
        return {"success": False, "error": "Donor or recipient inventory item missing"}

    if donor_item["current_stock"] < qty:
        return {"success": False, "error": f"Donor has insufficient stock ({donor_item['current_stock']} < {qty})"}

    # Apply transfer
    new_donor_stock = donor_item["current_stock"] - qty
    new_recip_stock = recip_item["current_stock"] + qty

    upd_donor = update_inventory_item(from_fac, med_id, new_donor_stock)
    upd_recip = update_inventory_item(to_fac, med_id, new_recip_stock)

    # Mark recommendation as executed
    target_rec["status"] = "EXECUTED"
    target_rec["executed_at"] = datetime.now().isoformat()
    recs[target_idx] = target_rec
    save_recommendations(recs)

    return {
        "success": True,
        "recommendation_id": recommendation_id,
        "transferred_units": qty,
        "medicine_id": med_id,
        "from_facility": from_fac,
        "to_facility": to_fac,
        "donor_post_stock": upd_donor["current_stock"],
        "recipient_post_stock": upd_recip["current_stock"],
        "donor_days_to_depletion": upd_donor["days_to_depletion"],
        "recipient_days_to_depletion": upd_recip["days_to_depletion"],
    }


def reset_to_seed_data() -> dict[str, Any]:
    """Wipe current state and re-seed with deterministic baseline data."""
    from seed.seed_data import write_seed_files
    write_seed_files(JSON_DATA_DIR)
    # Clear recommendations
    _save_json_file("recommendations.json", [])
    return {"status": "success", "message": "Store reset to clean deterministic seed data"}
