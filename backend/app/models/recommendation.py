"""Redistribution Recommendation Pydantic models."""

from typing import Optional
from pydantic import BaseModel, Field


class RedistributionRecommendation(BaseModel):
    id: str = Field(..., example="REC-FAC-003-FAC-002-MED-001")
    from_facility_id: str
    from_facility_name: str
    to_facility_id: str
    to_facility_name: str
    medicine_id: str
    medicine_name: str
    quantity: int = Field(..., gt=0)
    urgency: str = Field(default="HIGH")  # HIGH | MEDIUM | LOW
    strategy: str = Field(default="priority_greedy")
    projected_recipient_days: float
    projected_donor_days: float
    reason: str
    status: str = Field(default="PROPOSED")  # PROPOSED | EXECUTED
    created_at: Optional[str] = None


class OptimiserRunRequest(BaseModel):
    strategy: str = Field(default="priority_greedy", example="priority_greedy")  # priority_greedy | proportional_fairness
    min_transfer_units: int = Field(default=10, ge=1)


class ExecuteTransferRequest(BaseModel):
    recommendation_id: str
