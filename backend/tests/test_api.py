"""
Integration tests for MediStock REST API endpoints.

Tests:
  - Facilities listing
  - Inventory search & filtering
  - Consumption event recording & stock deduction
  - Demand spike simulation
  - Aggregate risk summary
  - Redistribution generation, execution, and stock balance transfer
  - Seed reset endpoint
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_facilities_endpoint():
    res = client.get("/api/facilities")
    assert res.status_code == 200
    facilities = res.json()
    assert len(facilities) >= 3
    ids = [f["id"] for f in facilities]
    assert "FAC-001" in ids
    assert "FAC-002" in ids


def test_inventory_listing():
    res = client.get("/api/inventory")
    assert res.status_code == 200
    items = res.json()
    assert len(items) >= 12


def test_inventory_filtering():
    # Filter by facility
    res_fac = client.get("/api/inventory?facility_id=FAC-001")
    assert res_fac.status_code == 200
    assert all(it["facility_id"] == "FAC-001" for it in res_fac.json())

    # Filter by category
    res_cat = client.get("/api/inventory?category=Antibiotics")
    assert res_cat.status_code == 200
    assert all(it["category"] == "Antibiotics" for it in res_cat.json())

    # Search filter
    res_search = client.get("/api/inventory?search=amoxicillin")
    assert res_search.status_code == 200
    assert len(res_search.json()) > 0


def test_risk_summary_endpoint():
    res = client.get("/api/risk/summary")
    assert res.status_code == 200
    data = res.json()
    assert "critical_count" in data
    assert "warning_count" in data
    assert "excess_count" in data
    assert "total_transferable_surplus_units" in data
    assert data["critical_count"] > 0
    assert data["excess_count"] > 0


def test_consume_and_spike_endpoints():
    # Record consumption
    consume_payload = {"units": 15.0, "reason": "Patient emergency discharge"}
    res = client.post("/api/inventory/FAC-001/MED-003/consume", json=consume_payload)
    assert res.status_code == 200
    assert res.json()["updated_inventory"] is not None

    # Simulate spike
    spike_payload = {"multiplier": 2.5, "duration_days": 3, "scenario_name": "Flu wave"}
    res_spike = client.post("/api/inventory/FAC-001/MED-003/spike", json=spike_payload)
    assert res_spike.status_code == 200
    assert res_spike.json()["spike_units_consumed"] > 0


def test_recommendations_and_execute_transfer():
    # Run optimiser
    run_payload = {"strategy": "priority_greedy", "min_transfer_units": 10}
    res_run = client.post("/api/recommendations/run", json=run_payload)
    assert res_run.status_code == 200
    data = res_run.json()
    assert data["recommendation_count"] > 0

    recs = data["recommendations"]
    target_rec = recs[0]
    rec_id = target_rec["id"]

    # Execute transfer
    exec_payload = {"recommendation_id": rec_id}
    res_exec = client.post("/api/recommendations/execute", json=exec_payload)
    assert res_exec.status_code == 200
    exec_data = res_exec.json()
    assert exec_data["success"] is True
    assert exec_data["transferred_units"] > 0


def test_seed_reset():
    res = client.post("/api/seed/reset")
    assert res.status_code == 200
    assert res.json()["status"] == "success"
