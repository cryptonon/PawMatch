"""Unit 2: Care Timeline.

Stores every care and medical event for a cat (vet visit, vaccination,
medication, foster stay, behavior note) on one dated timeline and returns
the entries in date order.
"""
import datetime as _dt
from dataclasses import dataclass

from app.errors import ValidationError

__all__ = ["CareEntry", "ValidationError", "add_entry", "timeline", "clear_store"]


@dataclass
class CareEntry:
    cat_id: int
    kind: str
    date: str
    note: str = ""
    end_date: str | None = None


_STORE: dict = {}


def clear_store():
    _STORE.clear()


def add_entry(cat_id, kind, date, note="", end_date=None):
    """Add one entry to a cat timeline. Dates are stored as ISO strings.

    Raises ValidationError when the date is missing, when the date is in
    the future, or when a medication ends before it starts.
    """
    if date is None or (isinstance(date, str) and date.strip() == ""):
        raise ValidationError("date is required")
    try:
        start = _dt.date.fromisoformat(str(date))
    except ValueError:
        raise ValidationError("date is not a valid date")
    if start > _dt.date.today():
        raise ValidationError("date cannot be in the future")
    if end_date is not None:
        try:
            end = _dt.date.fromisoformat(str(end_date))
        except ValueError:
            raise ValidationError("end_date is not a valid date")
        if end < start:
            raise ValidationError("end_date cannot be before date")
    entry = CareEntry(cat_id=cat_id, kind=kind, date=str(date), note=note, end_date=end_date)
    _STORE.setdefault(cat_id, []).append(entry)
    return entry


def timeline(cat_id):
    """All entries for one cat, sorted by date."""
    return sorted(_STORE.get(cat_id, []), key=lambda e: e.date)
