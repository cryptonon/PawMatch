"""Unit 8: Reminders and Follow-ups. Test code as specified in the unit test report."""
import pytest

from app.models import Application, Cat
from app.reminders.scheduler import (
    clear_store,
    due_reminders,
    finalize,
    mark_acted,
    next_checkin,
    overdue_reminders,
    register_application,
    schedule,
)


@pytest.fixture
def cat():
    clear_store()
    return Cat(id=1, name="Miso", age=2)


@pytest.fixture
def application():
    clear_store()
    app = Application(id=301, cat_id=1, adopter_name="Test Adopter")
    register_application(app)
    return app


def test_reminder_created_before_due_date(freezer, cat):
    freezer.move_to("2026-10-20")
    schedule(cat, kind="vaccination", due="2026-10-22")
    todays = due_reminders(on="2026-10-20")
    assert any(r.cat_id == cat.id and r.kind == "vaccination" for r in todays)


def test_unacted_reminder_moves_to_overdue(freezer, cat):
    schedule(cat, kind="vet_visit", due="2026-10-22")
    freezer.move_to("2026-10-23")
    overdue = overdue_reminders(on="2026-10-23")
    assert any(r.cat_id == cat.id for r in overdue)


def test_acted_reminder_does_not_reappear(freezer, cat):
    r = schedule(cat, kind="vaccination", due="2026-10-22")
    mark_acted(r.id)
    freezer.move_to("2026-10-25")
    assert overdue_reminders(on="2026-10-25") == []


def test_stalled_application_creates_reminder(freezer, application):
    application.stage = "screening"
    application.stage_since = "2026-10-10"
    freezer.move_to("2026-10-18")
    reminders = due_reminders(on="2026-10-18")
    assert any(r.application_id == application.id for r in reminders)


def test_checkin_scheduled_14_days_after_adoption(application):
    finalize(application, outcome="adopted", on="2026-10-01")
    checkin = next_checkin(application.id)
    assert checkin.due == "2026-10-15"


def test_checkin_not_due_early(freezer, application):
    finalize(application, outcome="adopted", on="2026-10-01")
    freezer.move_to("2026-10-14")
    assert due_reminders(on="2026-10-14") == []
