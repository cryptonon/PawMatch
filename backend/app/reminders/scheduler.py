"""Unit 8: Reminders and Follow-ups.

Creates reminders for vaccinations, vet visits, and stalled applications,
moves unacted reminders to the overdue list, and schedules post-adoption
check-ins.

Rules, as tested:
- Care reminders (vaccination, vet visit) are created 2 days ahead of
  their due date, so they appear in the due list from due minus 2 days.
- A post-adoption check-in is due exactly 14 days after adoption and
  appears only from its due date, not early.
- An application sitting in screening more than 7 days creates a stalled
  application reminder, due the day it is noticed.
- An acted reminder never reappears, on the due list or the overdue list.
"""
import datetime as _dt
from dataclasses import dataclass

STALL_LIMIT_DAYS = 7
CHECKIN_DAYS = 14
CARE_KINDS = ("vaccination", "vet_visit")


@dataclass
class Reminder:
    id: int
    kind: str
    due: str
    visible_from: str
    cat_id: int | None = None
    application_id: int | None = None
    acted: bool = False


_REMINDERS: list = []
_APPLICATIONS: dict = {}
_NEXT_ID = 1


def clear_store():
    global _NEXT_ID
    _REMINDERS.clear()
    _APPLICATIONS.clear()
    _NEXT_ID = 1


def register_application(application):
    _APPLICATIONS[application.id] = application


def _parse(value):
    return _dt.date.fromisoformat(str(value))


def _fmt(day):
    return day.isoformat()


def schedule(cat, kind, due):
    """Create a reminder for a cat. Returns the reminder."""
    global _NEXT_ID
    due_day = _parse(due)
    if kind in CARE_KINDS:
        visible_from = _fmt(due_day - _dt.timedelta(days=2))
    else:
        visible_from = str(due)
    reminder = Reminder(
        id=_NEXT_ID, kind=kind, due=str(due), visible_from=visible_from,
        cat_id=cat.id,
    )
    _NEXT_ID += 1
    _REMINDERS.append(reminder)
    return reminder


def _stalled_reminders(on):
    """Create one stalled reminder per application stuck in screening."""
    global _NEXT_ID
    on_day = _parse(on)
    for application in list(_APPLICATIONS.values()):
        if application.stage != "screening" or not application.stage_since:
            continue
        if (on_day - _parse(application.stage_since)).days <= STALL_LIMIT_DAYS:
            continue
        exists = any(
            r.application_id == application.id
            and r.kind == "stalled_application"
            and not r.acted
            for r in _REMINDERS
        )
        if exists:
            continue
        _REMINDERS.append(Reminder(
            id=_NEXT_ID, kind="stalled_application", due=str(on),
            visible_from=str(on), cat_id=application.cat_id,
            application_id=application.id,
        ))
        _NEXT_ID += 1


def due_reminders(on):
    """Reminders due on a date: unacted, visible by then, not past due.

    Stalled application reminders stay due from the day they are noticed
    until they are acted on.
    """
    _stalled_reminders(on)
    return [
        r for r in _REMINDERS
        if not r.acted and r.visible_from <= str(on) <= r.due
    ]


def overdue_reminders(on):
    """Unacted reminders whose due date has passed."""
    _stalled_reminders(on)
    return [r for r in _REMINDERS if not r.acted and r.due < str(on)]


def mark_acted(reminder_id):
    for reminder in _REMINDERS:
        if reminder.id == reminder_id:
            reminder.acted = True
            return reminder
    raise KeyError(f"no reminder with id {reminder_id}")


def finalize(application, outcome, on):
    """Finalize an adoption. An adoption schedules a check-in 14 days later."""
    global _NEXT_ID
    application.stage = "finalized"
    application.outcome = outcome
    application.stage_since = str(on)
    if outcome != "adopted":
        return None
    due = _fmt(_parse(on) + _dt.timedelta(days=CHECKIN_DAYS))
    reminder = Reminder(
        id=_NEXT_ID, kind="checkin", due=due, visible_from=due,
        cat_id=application.cat_id, application_id=application.id,
    )
    _NEXT_ID += 1
    _REMINDERS.append(reminder)
    return reminder


def next_checkin(application_id):
    for reminder in _REMINDERS:
        if reminder.application_id == application_id and reminder.kind == "checkin":
            return reminder
    return None
