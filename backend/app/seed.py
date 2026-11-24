"""Sample shelter data: cats, adopters, and applications.

Run from the backend folder: python -m app.seed

The data matches the known-answer fixture in the shelter metrics unit
tests, so the dashboard counts are the same here as there: 6 resident
cats, average stay 12.5 days, adoption rate 0.8, Pepper waiting longest.
One application is stuck in screening since 2026-10-10 for the stuck
list and the stalled reminder.
"""
import datetime as _dt

from app.models import Application, Cat
from app.reminders import scheduler
from app import store


def sample_cats():
    return [
        Cat(id=1, name="Pepper", age=12, breed="Domestic Shorthair", sex="F",
            arrival_date="2026-09-03", source="stray", health_status="healthy",
            behavior_notes="Calm and shy with visitors", temperament="calm",
            good_with_dogs=True, good_with_children=True, status="available"),
        Cat(id=2, name="Miso", age=2, breed="Domestic Shorthair", sex="F",
            arrival_date="2026-09-10", source="stray", health_status="healthy",
            behavior_notes="Friendly and playful", temperament="calm",
            good_with_dogs=True, good_with_children=True, status="available"),
        Cat(id=3, name="Luna", age=1, breed="Tabby", sex="F",
            arrival_date="2026-09-15", source="owner surrender", health_status="healthy",
            behavior_notes="Energetic and curious", temperament="energetic",
            good_with_dogs=True, good_with_children=False, status="available"),
        Cat(id=4, name="Simba", age=5, breed="Tabby", sex="M",
            arrival_date="2026-09-20", source="stray", health_status="healthy",
            behavior_notes="Energetic, loves toys", temperament="energetic",
            good_with_dogs=False, good_with_children=True, status="available"),
        Cat(id=5, name="Bella", age=8, breed="Siamese", sex="F",
            arrival_date="2026-10-01", source="stray", health_status="healthy",
            behavior_notes="Calm, likes quiet rooms", temperament="calm",
            good_with_dogs=False, good_with_children=True, status="available"),
        Cat(id=6, name="Oliver", age=3, breed="Domestic Shorthair", sex="M",
            arrival_date="2026-10-05", source="owner surrender", health_status="healthy",
            behavior_notes="Calm, good with dogs", temperament="calm",
            good_with_dogs=True, good_with_children=False, status="available"),
        Cat(id=7, name="Milo", age=4, breed="Tabby", sex="M",
            arrival_date="2026-08-01", source="stray", health_status="healthy",
            behavior_notes="Friendly", temperament="calm",
            good_with_dogs=True, good_with_children=True, status="adopted"),
        Cat(id=8, name="Hazel", age=6, breed="Domestic Shorthair", sex="F",
            arrival_date="2026-09-01", source="stray", health_status="healthy",
            behavior_notes="Shy, needs patience", temperament="calm",
            good_with_dogs=False, good_with_children=False, status="foster"),
    ]


def sample_applications():
    return [
        Application(id=101, cat_id=7, adopter_name="Adopter A", stage="finalized",
                    outcome="adopted", stay_days=5),
        Application(id=102, cat_id=2, adopter_name="Adopter B", stage="finalized",
                    outcome="adopted", stay_days=10),
        Application(id=103, cat_id=3, adopter_name="Adopter C", stage="finalized",
                    outcome="adopted", stay_days=15),
        Application(id=104, cat_id=4, adopter_name="Adopter D", stage="finalized",
                    outcome="adopted", stay_days=20),
        Application(id=105, cat_id=5, adopter_name="Adopter E", stage="closed",
                    outcome="withdrawn"),
        Application(id=106, cat_id=1, adopter_name="Adopter F", stage="submitted",
                    stage_since="2026-10-20"),
        Application(id=107, cat_id=6, adopter_name="Adopter G", stage="screening",
                    stage_since="2026-10-20"),
        Application(id=108, cat_id=1, adopter_name="Adopter H", stage="screening",
                    stage_since="2026-10-10"),
    ]


def seed_data():
    """Fill the store with the sample data. Returns the counts seeded."""
    store.reset()
    store.cats.extend(sample_cats())
    store.applications.extend(sample_applications())
    for application in store.applications:
        scheduler.register_application(application)
    return {"cats": len(store.cats), "applications": len(store.applications)}


if __name__ == "__main__":
    counts = seed_data()
    print(f"Seeded {counts['cats']} cats and {counts['applications']} applications.")
