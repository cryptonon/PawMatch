"""Unit 2: Care Timeline. Test code as specified in the unit test report."""
import pytest

from app.care.timeline import ValidationError, add_entry, clear_store, timeline
from app.models import Cat


@pytest.fixture
def cat():
    clear_store()
    return Cat(id=1, name="Miso", age=2)


def test_vaccination_entry_is_stored_with_its_date(cat):
    add_entry(cat.id, kind="vaccination", date="2026-09-14", note="FVRCP booster")
    entries = timeline(cat.id)
    assert len(entries) == 1
    assert entries[0].kind == "vaccination"
    assert entries[0].date == "2026-09-14"


def test_entries_come_back_in_date_order(cat):
    add_entry(cat.id, kind="vet_visit", date="2026-09-20", note="Checkup")
    add_entry(cat.id, kind="vaccination", date="2026-09-02", note="Rabies")
    add_entry(cat.id, kind="foster_stay", date="2026-09-10", note="Foster, 1 week")
    dates = [e.date for e in timeline(cat.id)]
    assert dates == ["2026-09-02", "2026-09-10", "2026-09-20"]


def test_medication_end_before_start_is_rejected(cat):
    with pytest.raises(ValidationError):
        add_entry(cat.id, kind="medication", date="2026-09-10",
                  end_date="2026-09-05", note="Antibiotic")


def test_entry_without_date_is_rejected(cat):
    with pytest.raises(ValidationError):
        add_entry(cat.id, kind="behavior_note", date=None, note="Shy with visitors")


def test_future_dated_entry_is_rejected(cat):
    with pytest.raises(ValidationError):
        add_entry(cat.id, kind="vet_visit", date="2999-01-01", note="Checkup")
