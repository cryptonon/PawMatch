"""Pydantic schemas for cat intake (Unit 1)."""
from pydantic import BaseModel, Field


class IntakeForm(BaseModel):
    name: str
    age: int = Field(ge=0, le=30)
    breed: str
    sex: str
    arrival_date: str
    source: str
    health_status: str = "healthy"
    behavior_notes: str = ""
