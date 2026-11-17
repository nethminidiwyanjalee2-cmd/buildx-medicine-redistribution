"""
Pure-Python Redistribution Optimiser for MediStock.

ISOLATION RULE: This module MUST NOT import firebase_admin, fastapi,
or any database/network modules.

Features:
  - Multi-facility bipartite matching between deficit (shortage) and surplus (excess) facilities.
  - Priority-based allocation: Most urgent deficits (CRITICAL, lowest days-to-depletion)
    are fulfilled first.
  - Compares strategies: 'priority_greedy' vs 'proportional_fairness'.
  - Human-interpretable reasoning strings explaining both sides of the transfer.
"""

from typing import Any


def recommend_redistribution(
    inventory_snapshot: list[dict[str, Any]],
    strategy: str = "priority_greedy",
    min_transfer_units: int = 10,
) -> list[dict[str, Any]]:
    """
    Generate redistribution transfer recommendations across all facilities.

    Each item in inventory_snapshot is expected to have:
      - facility_id: str
      - facility_name: str
      - medicine_id: str
      - medicine_name: str
      - current_stock: int/float
      - avg_daily_consumption: float
      - days_to_depletion: float
      - risk_level: str ("CRITICAL", "WARNING", "OK", "EXCESS")
      - deficit_units: int/float
      - surplus_units: int/float
    """
    if not inventory_snapshot:
        return []

    # Group items by medicine_id
    medicines_map: dict[str, list[dict[str, Any]]] = {}
    for item in inventory_snapshot:
        med_id = item.get("medicine_id")
        if med_id:
            medicines_map.setdefault(med_id, []).append(dict(item))

    recommendations: list[dict[str, Any]] = []

    for med_id, items in medicines_map.items():
        # Identify deficit and surplus sites for this medicine
        deficits = [
            it for it in items
            if it.get("risk_level") in ("CRITICAL", "WARNING") and it.get("deficit_units", 0) > 0
        ]
        surpluses = [
            it for it in items
            if it.get("risk_level") == "EXCESS" and it.get("surplus_units", 0) > 0
        ]

        if not deficits or not surpluses:
            continue

        # Sort deficits: CRITICAL first, then ascending days_to_depletion (most urgent first)
        deficits.sort(
            key=lambda d: (
                0 if d.get("risk_level") == "CRITICAL" else 1,
                float(d.get("days_to_depletion", 0.0)),
            )
        )

        # Sort surpluses: descending surplus_units (largest surplus donor first)
        surpluses.sort(key=lambda s: float(s.get("surplus_units", 0.0)), reverse=True)

        # Track mutable available surplus per donor
        donor_pool = {
            s["facility_id"]: {
                "available": float(s["surplus_units"]),
                "record": s,
            }
            for s in surpluses
        }

        if strategy == "proportional_fairness":
            total_surplus = sum(d["available"] for d in donor_pool.values())
            total_deficit = sum(float(d.get("deficit_units", 0)) for d in deficits)
            ratio = min(1.0, total_surplus / total_deficit) if total_deficit > 0 else 0.0

            for recipient in deficits:
                target_need = float(recipient.get("deficit_units", 0)) * ratio
                if target_need < min_transfer_units:
                    continue

                for donor_id, donor_data in donor_pool.items():
                    if donor_data["available"] <= 0:
                        continue
                    transfer_qty = min(target_need, donor_data["available"])
                    if transfer_qty >= min_transfer_units:
                        donor_data["available"] -= transfer_qty
                        target_need -= transfer_qty
                        reco = _build_recommendation(
                            donor=donor_data["record"],
                            recipient=recipient,
                            quantity=int(transfer_qty),
                            strategy="proportional_fairness",
                        )
                        recommendations.append(reco)
                    if target_need <= 0:
                        break

        else:  # priority_greedy
            for recipient in deficits:
                needed = float(recipient.get("deficit_units", 0))

                for donor_id, donor_data in donor_pool.items():
                    if donor_data["available"] <= 0 or needed <= 0:
                        continue

                    transfer_qty = min(needed, donor_data["available"])
                    if transfer_qty >= min_transfer_units:
                        donor_data["available"] -= transfer_qty
                        needed -= transfer_qty

                        reco = _build_recommendation(
                            donor=donor_data["record"],
                            recipient=recipient,
                            quantity=int(transfer_qty),
                            strategy="priority_greedy",
                        )
                        recommendations.append(reco)

    return recommendations


def _build_recommendation(
    donor: dict[str, Any],
    recipient: dict[str, Any],
    quantity: int,
    strategy: str,
) -> dict[str, Any]:
    """Helper to assemble a clear, structured recommendation payload with clinical reasoning."""
    medicine_name = recipient.get("medicine_name", donor.get("medicine_name", "Medicine"))
    recipient_name = recipient.get("facility_name", recipient.get("facility_id", "Recipient"))
    donor_name = donor.get("facility_name", donor.get("facility_id", "Donor"))
    rec_days = float(recipient.get("days_to_depletion", 0.0))
    donor_days = float(donor.get("days_to_depletion", 0.0))
    urgency = "HIGH" if recipient.get("risk_level") == "CRITICAL" else "MEDIUM"

    # Compute post-transfer projected days
    rec_burn = float(recipient.get("avg_daily_consumption", 1.0))
    donor_burn = float(donor.get("avg_daily_consumption", 1.0))

    new_rec_stock = float(recipient.get("current_stock", 0.0)) + quantity
    new_rec_days = round(new_rec_stock / rec_burn, 1) if rec_burn > 0 else 999.0

    new_donor_stock = max(0.0, float(donor.get("current_stock", 0.0)) - quantity)
    new_donor_days = round(new_donor_stock / donor_burn, 1) if donor_burn > 0 else 999.0

    reason = (
        f"Transfer {quantity:,} units of {medicine_name} from {donor_name} to {recipient_name}. "
        f"{recipient_name} has only {rec_days:.1f} days of stock remaining ({recipient.get('risk_level')}). "
        f"{donor_name} maintains {donor_days:.1f} days surplus. "
        f"Post-transfer: {recipient_name} extends runway to ~{new_rec_days:.1f} days; "
        f"{donor_name} retains a safe ~{new_donor_days:.1f} days."
    )

    return {
        "id": f"REC-{donor['facility_id']}-{recipient['facility_id']}-{recipient['medicine_id']}",
        "from_facility_id": donor["facility_id"],
        "from_facility_name": donor_name,
        "to_facility_id": recipient["facility_id"],
        "to_facility_name": recipient_name,
        "medicine_id": recipient["medicine_id"],
        "medicine_name": medicine_name,
        "quantity": quantity,
        "urgency": urgency,
        "strategy": strategy,
        "projected_recipient_days": new_rec_days,
        "projected_donor_days": new_donor_days,
        "reason": reason,
        "status": "PROPOSED",  # PROPOSED | EXECUTED
    }
