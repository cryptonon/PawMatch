"""Shared data models for PawMatch.

Plain dataclasses, so every unit works with the same Cat, Application,
AdopterProfile and Shelter shapes. Units import from here; tests build
fixtures from here.
"""
from dataclasses import dataclass, field


@dataclass
class Cat:
    id: int
    name: str
    age: int
    breed: str = "Domestic Shorthair"
    color: str = ""
    sex: str = "F"
    arrival_date: str = "2026-10-01"
    source: str = "stray"
    health_status: str = "healthy"
    behavior_notes: str | None = ""
    temperament: str = "calm"
    good_with_dogs: bool = True
    good_with_children: bool = True
    status: str = "available"  # available, adopted, foster
    stay_days: int | None = None
    was_long_stay: bool | None = None


@dataclass
class Application:
    id: int
    cat_id: int
    adopter_name: str = "Adopter"
    stage: str = "submitted"  # submitted, screening, meet_and_greet, approved, finalized, closed
    outcome: str | None = None  # adopted, returned, withdrawn
    stage_since: str | None = None
    stay_days: int | None = None


@dataclass
class Shelter:
    cats: list = field(default_factory=list)
    applications: list = field(default_factory=list)
