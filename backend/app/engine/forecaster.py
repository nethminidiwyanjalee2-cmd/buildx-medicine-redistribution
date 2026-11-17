"""
Consumption forecaster for MediStock.

STATUS: Phase 0 placeholder — do NOT implement logic here yet.

Phase 1 specification (see docs/PROJECT_CONTEXT.md §7.1):
  Input:
    consumption_history: list[dict]
      Each dict: {"date": str (ISO 8601), "units_consumed": int}
    current_stock: int
      Current stock level in units.

  Output:
    {
      "avg_daily_consumption": float,
      "days_to_depletion": float,   # math.inf if consumption == 0
      "forecast_method": str        # "weighted_moving_avg" | "simple_mean"
    }

  Algorithm:
    - If len(history) >= config.MIN_FORECAST_WINDOW:
        weighted moving average (linearly increasing weights, most-recent highest)
    - Else:
        simple arithmetic mean
    - days_to_depletion = current_stock / avg_daily_consumption

  This module MUST NOT import firebase_admin, fastapi, or any app.data module.
"""


def forecast(consumption_history: list, current_stock: int) -> dict:
    """
    Estimate average daily consumption and days until stock depletion.

    Not yet implemented — raises NotImplementedError in Phase 0.
    """
    raise NotImplementedError("forecaster.forecast() will be implemented in Phase 1.")
