"""
Deterministic Seed Data Generator for MediStock.

BuildX 0.1, Challenge 03.
Generates:
  - 4 Simulated Healthcare Facilities across Sri Lanka
  - 6 Essential Medicine Categories (12 unique pharmaceutical formulations)
  - 30 days of deterministic daily consumption history per facility/medicine pair
  - Deliberately structured imbalance scenarios:
      * Kandy Base Hospital faces imminent CRITICAL shortage of Amoxicillin (1.8 days left)
      * Galle General Hospital holds an EXCESS stockpile of Amoxicillin (46+ days left)
      * Colombo National Hospital has a WARNING on Insulin (4.5 days left)
      * Jaffna Teaching Hospital has surplus Insulin
"""

import json
import os
import random
from datetime import datetime, timedelta
from typing import Any

from app.config import JSON_DATA_DIR, CRITICAL_STOCK_DAYS, WARNING_STOCK_DAYS, EXCESS_STOCK_DAYS, TARGET_BUFFER_DAYS
from app.engine.forecaster import forecast
from app.engine.risk import classify_risk


FACILITIES: list[dict[str, str]] = [
    {
        "id": "FAC-001",
        "name": "Colombo National Hospital",
        "location": "Colombo, Western Province",
        "facility_type": "Tertiary National Referral Hospital",
        "contact_phone": "+94 11 269 1111",
        "contact_email": "pharmacy@cnh.health.gov.lk",
    },
    {
        "id": "FAC-002",
        "name": "Kandy Base Hospital",
        "location": "Kandy, Central Province",
        "facility_type": "Regional Base Hospital",
        "contact_phone": "+94 81 222 2261",
        "contact_email": "stores@kandybase.health.gov.lk",
    },
    {
        "id": "FAC-003",
        "name": "Galle General Hospital",
        "location": "Galle, Southern Province",
        "facility_type": "District General Hospital",
        "contact_phone": "+94 91 223 4271",
        "contact_email": "logistics@gallehosp.health.gov.lk",
    },
    {
        "id": "FAC-004",
        "name": "Jaffna Teaching Hospital",
        "location": "Jaffna, Northern Province",
        "facility_type": "Provincial Teaching Hospital",
        "contact_phone": "+94 21 222 2262",
        "contact_email": "medstores@jth.health.gov.lk",
    },
]

MEDICINES: list[dict[str, Any]] = [
    {
        "id": "MED-001",
        "name": "Amoxicillin 500mg",
        "category": "Antibiotics",
        "dosage_form": "Capsule",
        "unit": "capsules",
        "base_burn_rate": 80.0,
        "reorder_level": 500.0,
    },
    {
        "id": "MED-002",
        "name": "Ciprofloxacin 500mg",
        "category": "Antibiotics",
        "dosage_form": "Tablet",
        "unit": "tablets",
        "base_burn_rate": 45.0,
        "reorder_level": 300.0,
    },
    {
        "id": "MED-003",
        "name": "Paracetamol 500mg",
        "category": "Analgesics & Antipyretics",
        "dosage_form": "Tablet",
        "unit": "tablets",
        "base_burn_rate": 220.0,
        "reorder_level": 1500.0,
    },
    {
        "id": "MED-004",
        "name": "Ibuprofen 400mg",
        "category": "Analgesics & Antipyretics",
        "dosage_form": "Tablet",
        "unit": "tablets",
        "base_burn_rate": 60.0,
        "reorder_level": 400.0,
    },
    {
        "id": "MED-005",
        "name": "Amlodipine 5mg",
        "category": "Cardiovascular",
        "dosage_form": "Tablet",
        "unit": "tablets",
        "base_burn_rate": 90.0,
        "reorder_level": 600.0,
    },
    {
        "id": "MED-006",
        "name": "Atorvastatin 20mg",
        "category": "Cardiovascular",
        "dosage_form": "Tablet",
        "unit": "tablets",
        "base_burn_rate": 75.0,
        "reorder_level": 500.0,
    },
    {
        "id": "MED-007",
        "name": "Metformin 500mg",
        "category": "Antidiabetic",
        "dosage_form": "Tablet",
        "unit": "tablets",
        "base_burn_rate": 130.0,
        "reorder_level": 900.0,
    },
    {
        "id": "MED-008",
        "name": "Human Regular Insulin 100IU/ml",
        "category": "Antidiabetic",
        "dosage_form": "Vial 10ml",
        "unit": "vials",
        "base_burn_rate": 20.0,
        "reorder_level": 150.0,
    },
    {
        "id": "MED-009",
        "name": "Salbutamol Inhaler 100mcg",
        "category": "Respiratory",
        "dosage_form": "Inhaler (200 doses)",
        "unit": "canisters",
        "base_burn_rate": 25.0,
        "reorder_level": 180.0,
    },
    {
        "id": "MED-010",
        "name": "Montelukast 10mg",
        "category": "Respiratory",
        "dosage_form": "Tablet",
        "unit": "tablets",
        "base_burn_rate": 40.0,
        "reorder_level": 280.0,
    },
    {
        "id": "MED-011",
        "name": "Adrenaline 1mg/ml Ampoule",
        "category": "Emergency & Critical Care",
        "dosage_form": "Injection Ampoule",
        "unit": "ampoules",
        "base_burn_rate": 10.0,
        "reorder_level": 70.0,
    },
    {
        "id": "MED-012",
        "name": "Dextrose 50% Infusion 50ml",
        "category": "Emergency & Critical Care",
        "dosage_form": "IV Infusion Bottle",
        "unit": "bottles",
        "base_burn_rate": 15.0,
        "reorder_level": 100.0,
    },
]


def generate_seed_dataset(days_of_history: int = 30) -> dict[str, Any]:
    """
    Generate fully deterministic dataset with 4 facilities, 12 medicines,
    and realistic days-to-depletion and consumption logs.
    """
    rng = random.Random(42)  # Fixed seed for strict determinism
    base_date = datetime(2026, 11, 17)

    all_logs: list[dict[str, Any]] = []
    inventory_items: list[dict[str, Any]] = []

    facility_scale = {
        "FAC-001": 1.4,  # High consumption (tertiary)
        "FAC-002": 0.9,  # Moderate consumption
        "FAC-003": 0.8,  # Moderate consumption
        "FAC-004": 1.0,  # Baseline
    }

    for fac in FACILITIES:
        fac_id = fac["id"]
        scale = facility_scale.get(fac_id, 1.0)

        for med in MEDICINES:
            med_id = med["id"]
            nominal_burn = med["base_burn_rate"] * scale

            # Generate historical logs for past N days
            med_logs = []
            for d in range(days_of_history, 0, -1):
                date_str = (base_date - timedelta(days=d)).strftime("%Y-%m-%d")
                # Daily variation +/- 25% with noise
                factor = rng.uniform(0.75, 1.25)
                consumed = max(1, round(nominal_burn * factor))
                med_logs.append({
                    "facility_id": fac_id,
                    "medicine_id": med_id,
                    "date": date_str,
                    "units_consumed": consumed,
                })
            all_logs.extend(med_logs)

            # Forecast burn rate using engine forecaster
            fc = forecast(med_logs, current_stock=0.0)
            avg_burn = fc["avg_daily_consumption"]

            # Set current_stock to create realistic imbalances
            if fac_id == "FAC-002" and med_id == "MED-001":
                # Kandy Amoxicillin: CRITICAL shortage (1.8 days)
                current_stock = round(avg_burn * 1.8)
            elif fac_id == "FAC-003" and med_id == "MED-001":
                # Galle Amoxicillin: EXCESS surplus (46.0 days)
                current_stock = round(avg_burn * 46.0)
            elif fac_id == "FAC-001" and med_id == "MED-008":
                # Colombo Insulin: WARNING shortage (4.5 days)
                current_stock = round(avg_burn * 4.5)
            elif fac_id == "FAC-004" and med_id == "MED-008":
                # Jaffna Insulin: EXCESS surplus (38.0 days)
                current_stock = round(avg_burn * 38.0)
            elif fac_id == "FAC-004" and med_id == "MED-011":
                # Jaffna Adrenaline: CRITICAL shortage (2.2 days)
                current_stock = round(avg_burn * 2.2)
            elif fac_id == "FAC-001" and med_id == "MED-011":
                # Colombo Adrenaline: EXCESS surplus (35.0 days)
                current_stock = round(avg_burn * 35.0)
            else:
                # Normal stable operating stock (between 12 and 22 days)
                days_factor = rng.uniform(12.0, 22.0)
                current_stock = round(avg_burn * days_factor)

            # Classify risk
            reorder = round(med["reorder_level"] * scale)
            days_left = round(current_stock / avg_burn, 1) if avg_burn > 0 else 999.0
            risk_info = classify_risk(
                inventory_item={
                    "current_stock": current_stock,
                    "avg_daily_consumption": avg_burn,
                    "days_to_depletion": days_left,
                    "reorder_level": reorder,
                    "medicine_name": med["name"],
                    "facility_name": fac["name"],
                },
                critical_days=CRITICAL_STOCK_DAYS,
                warning_days=WARNING_STOCK_DAYS,
                excess_days=EXCESS_STOCK_DAYS,
                target_buffer_days=TARGET_BUFFER_DAYS,
            )

            inventory_items.append({
                "facility_id": fac_id,
                "facility_name": fac["name"],
                "medicine_id": med_id,
                "medicine_name": med["name"],
                "category": med["category"],
                "dosage_form": med["dosage_form"],
                "unit": med["unit"],
                "current_stock": current_stock,
                "reorder_level": reorder,
                "avg_daily_consumption": avg_burn,
                "days_to_depletion": risk_info["days_to_depletion"],
                "risk_level": risk_info["risk_level"],
                "deficit_units": risk_info["deficit_units"],
                "surplus_units": risk_info["surplus_units"],
                "trend": fc["trend"],
                "last_updated": datetime.now().isoformat(),
                "reason": risk_info["reason"],
            })

    return {
        "facilities": FACILITIES,
        "medicines": MEDICINES,
        "inventory": inventory_items,
        "consumption_logs": all_logs,
        "generated_at": datetime.now().isoformat(),
    }


def write_seed_files(dest_dir: str = JSON_DATA_DIR) -> None:
    """Write generated seed data to json_store directory."""
    os.makedirs(dest_dir, exist_ok=True)
    dataset = generate_seed_dataset()

    for key in ("facilities", "medicines", "inventory", "consumption_logs"):
        filepath = os.path.join(dest_dir, f"{key}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(dataset[key], f, indent=2)

    meta_file = os.path.join(dest_dir, "metadata.json")
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump({
            "version": "1.0.0",
            "seed": 42,
            "generated_at": dataset["generated_at"],
            "facility_count": len(dataset["facilities"]),
            "inventory_count": len(dataset["inventory"]),
            "log_count": len(dataset["consumption_logs"]),
        }, f, indent=2)


if __name__ == "__main__":
    write_seed_files()
    print("Deterministic seed dataset written successfully to JSON store.")
