"""
Pure-Python Consumption Forecaster for MediStock.

ISOLATION RULE: This module MUST NOT import firebase_admin, fastapi,
or any database/network modules.

Calculates:
  - Average daily consumption using weighted moving average (recent days weighted higher)
    or simple arithmetic mean when history < MIN_FORECAST_WINDOW.
  - Trend direction (increasing, stable, decreasing) by comparing recent half vs older half.
  - Estimated days before stock depletion (current_stock / avg_daily_consumption).
"""

from typing import Any


def calculate_daily_consumption(
    consumption_history: list[dict[str, Any]],
    min_window: int = 7,
    max_window: int = 30,
) -> dict[str, Any]:
    """
    Calculate the forecasted average daily consumption from a list of logs.

    Each log item must have at least 'units_consumed' (int or float).
    Optional 'date' field (ISO string) can be used for ordering.
    """
    if not consumption_history:
        return {
            "avg_daily_consumption": 0.0,
            "forecast_method": "no_data",
            "sample_size": 0,
            "trend": "unknown",
            "volatility": 0.0,
        }

    # Sort by date if present
    sorted_history = sorted(
        consumption_history,
        key=lambda item: str(item.get("date", "")),
    )

    # Restrict to maximum window
    window = sorted_history[-max_window:] if len(sorted_history) > max_window else sorted_history
    units = [float(x.get("units_consumed", 0.0)) for x in window]
    n = len(units)

    if n == 0 or all(u == 0.0 for u in units):
        return {
            "avg_daily_consumption": 0.0,
            "forecast_method": "zero_consumption",
            "sample_size": n,
            "trend": "stable",
            "volatility": 0.0,
        }

    if n < min_window:
        # Simple arithmetic mean
        avg = sum(units) / n
        method = "simple_mean"
    else:
        # Linearly increasing weights (e.g. 1, 2, ..., n)
        weights = list(range(1, n + 1))
        weight_sum = sum(weights)
        avg = sum(u * w for u, w in zip(units, weights)) / weight_sum
        method = "weighted_moving_average"

    # Analyze consumption trend
    if n >= 4:
        midpoint = n // 2
        first_half = units[:midpoint]
        second_half = units[midpoint:]
        mean_first = sum(first_half) / len(first_half) if first_half else 0.0
        mean_second = sum(second_half) / len(second_half) if second_half else 0.0

        if mean_second > mean_first * 1.15:
            trend = "increasing"
        elif mean_second < mean_first * 0.85:
            trend = "decreasing"
        else:
            trend = "stable"
    else:
        trend = "stable"

    # Simple sample standard deviation
    mean = sum(units) / n
    variance = sum((u - mean) ** 2 for u in units) / n
    volatility = round(variance ** 0.5, 2)

    return {
        "avg_daily_consumption": round(avg, 2),
        "forecast_method": method,
        "sample_size": n,
        "trend": trend,
        "volatility": volatility,
    }


def estimate_days_to_depletion(current_stock: float, avg_daily_consumption: float) -> float:
    """
    Estimate number of days before stock is completely depleted.

    Returns float('inf') if consumption is 0 or negative.
    """
    if current_stock <= 0:
        return 0.0
    if avg_daily_consumption <= 0:
        return float("inf")
    return round(current_stock / avg_daily_consumption, 1)


def forecast(
    consumption_history: list[dict[str, Any]],
    current_stock: float,
    min_window: int = 7,
    max_window: int = 30,
) -> dict[str, Any]:
    """
    Complete forecast pipeline: returns daily rate, days-to-depletion, and confidence.
    """
    analysis = calculate_daily_consumption(
        consumption_history,
        min_window=min_window,
        max_window=max_window,
    )
    burn_rate = analysis["avg_daily_consumption"]
    days_left = estimate_days_to_depletion(current_stock, burn_rate)

    return {
        "current_stock": current_stock,
        "avg_daily_consumption": burn_rate,
        "days_to_depletion": days_left,
        "forecast_method": analysis["forecast_method"],
        "sample_size": analysis["sample_size"],
        "trend": analysis["trend"],
        "volatility": analysis["volatility"],
    }
