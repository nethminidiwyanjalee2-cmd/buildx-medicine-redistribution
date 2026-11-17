"""
Unit tests for Pure-Python Forecaster Engine.

Tests:
  - Empty history & zero consumption handling
  - Simple mean fallback for small sample sizes (< MIN_FORECAST_WINDOW)
  - Linearly weighted moving average for >= MIN_FORECAST_WINDOW
  - Days-to-depletion division & infinity handling
  - Trend detection (increasing, stable, decreasing)
"""

import math
from app.engine.forecaster import (
    calculate_daily_consumption,
    estimate_days_to_depletion,
    forecast,
)


def test_empty_consumption_history():
    res = calculate_daily_consumption([])
    assert res["avg_daily_consumption"] == 0.0
    assert res["forecast_method"] == "no_data"


def test_zero_consumption():
    history = [{"date": f"2026-11-0{i}", "units_consumed": 0} for i in range(1, 8)]
    res = calculate_daily_consumption(history)
    assert res["avg_daily_consumption"] == 0.0
    assert res["forecast_method"] == "zero_consumption"


def test_simple_mean_under_min_window():
    # 3 days (< 7)
    history = [
        {"date": "2026-11-01", "units_consumed": 20},
        {"date": "2026-11-02", "units_consumed": 30},
        {"date": "2026-11-03", "units_consumed": 40},
    ]
    res = calculate_daily_consumption(history, min_window=7)
    assert res["forecast_method"] == "simple_mean"
    assert res["avg_daily_consumption"] == 30.0


def test_weighted_moving_average():
    # 7 days with increasing weights
    # Weights: 1, 2, 3, 4, 5, 6, 7 (sum = 28)
    # Units: 10, 10, 10, 10, 10, 10, 20
    # Weighted sum: 10*1 + 10*2 + 10*3 + 10*4 + 10*5 + 10*6 + 20*7 = 210 + 140 = 350
    # 350 / 28 = 12.5
    history = [
        {"date": f"2026-11-0{i}", "units_consumed": 10 if i < 7 else 20}
        for i in range(1, 8)
    ]
    res = calculate_daily_consumption(history, min_window=7)
    assert res["forecast_method"] == "weighted_moving_average"
    assert res["avg_daily_consumption"] == 12.5


def test_days_to_depletion_calculation():
    assert estimate_days_to_depletion(100.0, 20.0) == 5.0
    assert estimate_days_to_depletion(0.0, 20.0) == 0.0
    assert math.isinf(estimate_days_to_depletion(100.0, 0.0))


def test_trend_detection_increasing():
    # First half = 10, second half = 50
    history = [
        {"date": f"2026-11-0{i}", "units_consumed": 10 if i <= 4 else 50}
        for i in range(1, 9)
    ]
    res = calculate_daily_consumption(history)
    assert res["trend"] == "increasing"


def test_full_forecast_pipeline():
    history = [{"date": f"2026-11-0{i}", "units_consumed": 25} for i in range(1, 8)]
    res = forecast(history, current_stock=100.0)
    assert res["avg_daily_consumption"] == 25.0
    assert res["days_to_depletion"] == 4.0
    assert res["trend"] == "stable"
