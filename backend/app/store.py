"""In-memory store for the FastAPI app.

The unit tests use no running server and no database. The API keeps the
same rule: one process holds the cats, applications, care entries, and
reminders in memory, and seed data fills it. Tests reset the store
between runs.
"""
from app.bios import drafting as bio_drafting
from app.care import timeline as care_timeline
from app.models import Shelter
from app.reminders import scheduler

cats = []
applications = []


def reset():
    cats.clear()
    applications.clear()
    care_timeline.clear_store()
    scheduler.clear_store()
    bio_drafting.clear_store()


def shelter():
    return Shelter(cats=list(cats), applications=list(applications))
