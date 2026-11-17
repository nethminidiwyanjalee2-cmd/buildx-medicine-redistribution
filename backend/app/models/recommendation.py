"""
Redistribution recommendation Pydantic model.

STATUS: Phase 0 placeholder.

Phase 2 implementation:
  class RedistributionRecommendation(BaseModel):
      from_facility: str
      to_facility: str
      medicine_id: str
      quantity: int
      urgency: Literal["high", "medium", "low"]
      reason: str
      created_at: datetime

  See docs/PROJECT_CONTEXT.md §5.4 for the full data model.
"""

# Phase 2: uncomment and implement.
# from pydantic import BaseModel
# from datetime import datetime
# from typing import Literal
# class RedistributionRecommendation(BaseModel):
#     ...
