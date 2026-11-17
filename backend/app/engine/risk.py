"""
Pure-Python Stock Risk Classifier for MediStock.

ISOLATION RULE: This module MUST NOT import firebase_admin, fastapi,
or any database/network modules.

Classifies stock status:
  - CRITICAL: days_to_depletion < critical_days (or current_stock == 0)
  - WARNING:  days_to_depletion < warning_days
  - EXCESS:   days_to_depletion > excess_days and current_stock > reorder_level
  - OK:       normal operating range

Also computes:
  - deficit_units: quantity needed to reach a safe operating buffer (target_buffer_days)
  - surplus_units: transferable quantity above the safe retention threshold
  - clinical reasoning string for transparency
"""

import math
from typing import Any


def classify_risk(
    inventory_item: dict[str, Any],
    critical_days: float = 3.0,
    warning_days: float = 7.0,
    excess_days: float = 30.0,
    target_buffer_days: float = 14.0,
) -> dict[str, Any]:
    """
    Classify the risk level of an inventory item and calculate surplus/deficit.

    Expected keys in inventory_item:
      - current_stock (float or int)
      - avg_daily_consumption (float)
      - days_to_depletion (float or inf)
      - reorder_level (optional, float or int)
      - medicine_name (optional, str)
      - facility_name (optional, str)
    """
    current_stock = float(inventory_item.get("current_stock", 0.0))
    avg_burn = float(inventory_item.get("avg_daily_consumption", 0.0))
    days_left = inventory_item.get("days_to_depletion", float("inf"))
    reorder_level = float(inventory_item.get("reorder_level", 0.0))
    medicine = inventory_item.get("medicine_name", "Medicine")
    facility = inventory_item.get("facility_name", "Facility")

    # If days_to_depletion was not pre-calculated
    if days_left is None:
        if current_stock <= 0:
            days_left = 0.0
        elif avg_burn > 0:
            days_left = round(current_stock / avg_burn, 1)
        else:
            days_left = float("inf")

    # Determine Risk Category
    if current_stock <= 0:
        risk_level = "CRITICAL"
        reason = f"Stockout detected at {facility}. Zero units of {medicine} remaining."
    elif days_left < critical_days:
        risk_level = "CRITICAL"
        reason = (
            f"Critical shortage at {facility}: {days_left:.1f} days of {medicine} remaining "
            f"(threshold: <{critical_days:.0f} days). Emergency stockout imminent."
        )
    elif days_left < warning_days:
        risk_level = "WARNING"
        reason = (
            f"Low stock warning at {facility}: {days_left:.1f} days remaining "
            f"(threshold: <{warning_days:.0f} days). Reorder or redistribution required."
        )
    elif days_left > excess_days and current_stock > reorder_level:
        risk_level = "EXCESS"
        reason = (
            f"Excess inventory at {facility}: {days_left:.1f} days of supply on hand "
            f"(exceeds {excess_days:.0f}-day upper bound). Stock can be safely transferred."
        )
    else:
        risk_level = "OK"
        reason = (
            f"Stable inventory at {facility}: {days_left:.1f} days of supply "
            f"maintains adequate operational safety margin."
            if not math.isinf(days_left)
            else f"Stable stock at {facility}. Zero active consumption recorded."
        )

    # Calculate Deficit Units (units needed to reach target safe buffer)
    deficit_units = 0.0
    if risk_level in ("CRITICAL", "WARNING"):
        target_units = max(avg_burn * target_buffer_days, reorder_level)
        deficit_units = max(0.0, round(target_units - current_stock, 0))

    # Calculate Surplus Units (units safely transferable while retaining excess_days or target_buffer_days)
    surplus_units = 0.0
    if risk_level == "EXCESS":
        # Keep a safe operational buffer (e.g. 14 days or reorder level), rest is transferable
        retained_stock = max(avg_burn * target_buffer_days, reorder_level)
        surplus_units = max(0.0, round(current_stock - retained_stock, 0))

    return {
        "risk_level": risk_level,
        "days_to_depletion": days_left if not math.isinf(days_left) else 999.0,
        "is_infinite": math.isinf(days_left),
        "deficit_units": int(deficit_units),
        "surplus_units": int(surplus_units),
        "reason": reason,
    }
