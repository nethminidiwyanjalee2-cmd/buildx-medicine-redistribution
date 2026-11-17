"""Inventory & Consumption Pydantic models."""

from typing import Optional
from pydantic import BaseModel, Field


class ConsumptionRecord(BaseModel):
    date: str = Field(..., example="2026-11-16")
    units_consumed: float = Field(..., ge=0, example=45.0)


class ConsumptionLogEntry(BaseModel):
    facility_id: str
    medicine_id: str
    date: str
    units_consumed: float


class InventoryItem(BaseModel):
    facility_id: str = Field(..., example="FAC-001")
    facility_name: str = Field(..., example="Colombo National Hospital")
    medicine_id: str = Field(..., example="MED-001")
    medicine_name: str = Field(..., example="Amoxicillin 500mg")
    category: str = Field(..., example="Antibiotics")
    dosage_form: str = Field(default="Capsule")
    unit: str = Field(default="capsule")
    current_stock: float = Field(..., ge=0, example=1200.0)
    reorder_level: float = Field(default=500.0, ge=0)
    avg_daily_consumption: float = Field(default=0.0, ge=0)
    days_to_depletion: float = Field(default=0.0)
    risk_level: str = Field(default="OK")  # CRITICAL | WARNING | OK | EXCESS
    deficit_units: int = Field(default=0)
    surplus_units: int = Field(default=0)
    trend: str = Field(default="stable")
    last_updated: Optional[str] = None
    reason: Optional[str] = None


class ConsumeRequest(BaseModel):
    units: float = Field(..., gt=0, example=25.0)
    date: Optional[str] = None
    reason: Optional[str] = "Routine daily dispensing"


class DemandSpikeRequest(BaseModel):
    multiplier: float = Field(default=2.5, gt=1.0, le=10.0, example=3.0)
    duration_days: int = Field(default=5, ge=1, le=30, example=5)
    scenario_name: str = Field(default="Seasonal Outbreak")
