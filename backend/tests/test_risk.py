"""
Unit tests for Pure-Python Risk Classifier Engine.

Tests:
  - CRITICAL risk (< 3 days or stockout)
  - WARNING risk (< 7 days)
  - OK risk (normal range)
  - EXCESS risk (> 30 days)
  - Deficit and surplus unit calculations
"""

from app.engine.risk import classify_risk


def test_classify_stockout():
    item = {
        "current_stock": 0,
        "avg_daily_consumption": 20.0,
        "days_to_depletion": 0.0,
        "reorder_level": 100.0,
        "medicine_name": "Amoxicillin",
        "facility_name": "Kandy Base Hospital",
    }
    res = classify_risk(item, critical_days=3.0, warning_days=7.0, target_buffer_days=14.0)
    assert res["risk_level"] == "CRITICAL"
    assert res["days_to_depletion"] == 0.0
    assert res["deficit_units"] > 0
    assert "Stockout" in res["reason"]


def test_classify_critical():
    item = {
        "current_stock": 40.0,
        "avg_daily_consumption": 20.0,
        "days_to_depletion": 2.0,
        "reorder_level": 100.0,
    }
    res = classify_risk(item, critical_days=3.0, warning_days=7.0, target_buffer_days=14.0)
    assert res["risk_level"] == "CRITICAL"
    # Deficit should aim for target buffer of 14 days = 280 units -> 280 - 40 = 240 units
    assert res["deficit_units"] == 240
    assert res["surplus_units"] == 0


def test_classify_warning():
    item = {
        "current_stock": 100.0,
        "avg_daily_consumption": 20.0,
        "days_to_depletion": 5.0,
        "reorder_level": 50.0,
    }
    res = classify_risk(item, critical_days=3.0, warning_days=7.0, target_buffer_days=14.0)
    assert res["risk_level"] == "WARNING"
    assert res["deficit_units"] == 180  # 14 * 20 = 280; 280 - 100 = 180
    assert res["surplus_units"] == 0


def test_classify_ok():
    item = {
        "current_stock": 300.0,
        "avg_daily_consumption": 20.0,
        "days_to_depletion": 15.0,
        "reorder_level": 100.0,
    }
    res = classify_risk(item, critical_days=3.0, warning_days=7.0, excess_days=30.0)
    assert res["risk_level"] == "OK"
    assert res["deficit_units"] == 0
    assert res["surplus_units"] == 0


def test_classify_excess():
    item = {
        "current_stock": 900.0,
        "avg_daily_consumption": 20.0,
        "days_to_depletion": 45.0,
        "reorder_level": 100.0,
    }
    res = classify_risk(
        item,
        critical_days=3.0,
        warning_days=7.0,
        excess_days=30.0,
        target_buffer_days=14.0,
    )
    assert res["risk_level"] == "EXCESS"
    # Safe retained buffer = 14 * 20 = 280 units
    # Transferable surplus = 900 - 280 = 620 units
    assert res["surplus_units"] == 620
    assert res["deficit_units"] == 0
    assert "Excess" in res["reason"]
