"""Pydantic schemas and the adopter profile model (Unit 4)."""
from dataclasses import dataclass


@dataclass
class AdopterProfile:
    has_dog: bool = False
    has_children: bool = False
    home_type: str | None = "house"
    preferred_temperament: str | None = None
    experience: str = "first_time"  # first_time or experienced
    wants_senior: bool = False
