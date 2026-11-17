"""
Unit tests for Pure-Python Redistribution Optimiser Engine.

Tests:
  - Matching deficit hospital with surplus donor
  - Quantity calculation: min(deficit, surplus)
  - Priority ordering: Critical deficit matched before Warning
  - Projected runway calculation in recommendation reason
  - Proportional vs Greedy strategy comparisons
"""

from app.engine.optimiser import recommend_redistribution


def test_single_pair_redistribution():
    snapshot = [
        {
            "facility_id": "FAC-002",
            "facility_name": "Kandy Base Hospital",
            "medicine_id": "MED-001",
            "medicine_name": "Amoxicillin 500mg",
            "current_stock": 50,
            "avg_daily_consumption": 25.0,
            "days_to_depletion": 2.0,
            "risk_level": "CRITICAL",
            "deficit_units": 300,
            "surplus_units": 0,
        },
        {
            "facility_id": "FAC-003",
            "facility_name": "Galle General Hospital",
            "medicine_id": "MED-001",
            "medicine_name": "Amoxicillin 500mg",
            "current_stock": 1000,
            "avg_daily_consumption": 20.0,
            "days_to_depletion": 50.0,
            "risk_level": "EXCESS",
            "deficit_units": 0,
            "surplus_units": 720,
        },
    ]

    recs = recommend_redistribution(snapshot, strategy="priority_greedy")
    assert len(recs) == 1
    r = recs[0]
    assert r["from_facility_id"] == "FAC-003"
    assert r["to_facility_id"] == "FAC-002"
    assert r["medicine_id"] == "MED-001"
    assert r["quantity"] == 300
    assert r["urgency"] == "HIGH"
    assert "Transfer 300 units" in r["reason"]
    assert r["projected_recipient_days"] > 2.0


def test_no_recommendation_when_no_surplus():
    snapshot = [
        {
            "facility_id": "FAC-002",
            "medicine_id": "MED-001",
            "risk_level": "CRITICAL",
            "deficit_units": 300,
            "surplus_units": 0,
        },
        {
            "facility_id": "FAC-001",
            "medicine_id": "MED-001",
            "risk_level": "OK",
            "deficit_units": 0,
            "surplus_units": 0,
        },
    ]
    recs = recommend_redistribution(snapshot)
    assert len(recs) == 0


def test_priority_ordering_critical_over_warning():
    snapshot = [
        {
            "facility_id": "FAC-A",
            "facility_name": "Hospital A",
            "medicine_id": "MED-001",
            "days_to_depletion": 5.0,
            "risk_level": "WARNING",
            "deficit_units": 200,
            "surplus_units": 0,
        },
        {
            "facility_id": "FAC-B",
            "facility_name": "Hospital B",
            "medicine_id": "MED-001",
            "days_to_depletion": 1.5,
            "risk_level": "CRITICAL",
            "deficit_units": 200,
            "surplus_units": 0,
        },
        {
            "facility_id": "FAC-C",
            "facility_name": "Hospital C",
            "medicine_id": "MED-001",
            "days_to_depletion": 40.0,
            "risk_level": "EXCESS",
            "deficit_units": 0,
            "surplus_units": 250,  # Only enough for one full deficit
        },
    ]
    recs = recommend_redistribution(snapshot, strategy="priority_greedy")
    # First recommendation MUST serve FAC-B (CRITICAL)
    assert len(recs) >= 1
    assert recs[0]["to_facility_id"] == "FAC-B"
    assert recs[0]["quantity"] == 200
