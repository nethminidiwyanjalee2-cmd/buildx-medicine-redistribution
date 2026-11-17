"""Facility Pydantic models."""

from pydantic import BaseModel, Field


class FacilityBase(BaseModel):
    id: str = Field(..., example="FAC-001")
    name: str = Field(..., example="Colombo National Hospital")
    location: str = Field(..., example="Colombo, Western Province")
    facility_type: str = Field(default="Tertiary Referral Hospital")
    contact_phone: str = Field(default="+94 11 269 1111")
    contact_email: str = Field(default="pharmacy@cnh.health.gov.lk")


class Facility(FacilityBase):
    pass
