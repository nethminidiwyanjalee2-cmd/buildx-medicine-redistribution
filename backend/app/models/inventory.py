"""
Inventory Pydantic models.

STATUS: Phase 0 placeholder.

Phase 1 implementation:
  class InventoryItem(BaseModel):
      facility_id: str
      medicine_id: str
      medicine_name: str
      category: str
      current_stock_units: int
      unit: str
      reorder_level_units: int
      last_updated: datetime

  class ConsumptionEvent(BaseModel):
      facility_id: str
      medicine_id: str
      date: str  # ISO 8601 date
      units_consumed: int

  See docs/PROJECT_CONTEXT.md §5.2 and §5.3 for the full data model.
"""

# Phase 1: uncomment and implement.
# from pydantic import BaseModel
# from datetime import datetime
# class InventoryItem(BaseModel):
#     ...
