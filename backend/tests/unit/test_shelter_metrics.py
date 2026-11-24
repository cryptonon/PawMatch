"""Unit 7: Shelter Metrics. Test code as specified in the unit test report."""
import pytest

from app.metrics.dashboard import metrics
from app.models import Application, Cat, Shelter


@pytest.fixture
def shelter():
    # 8 cat records: 6 resident, 1 adopted, 1 in foster care off site.
    # 5 closed applications: 4 adopted (stays 5, 10, 15, 20 days),
    # 1 withdrawn. 2 open applications must not count.
    cats = [
        Cat(id=1, name="Pepper", age=12, arrival_date="2026-09-03", status="available"),
        Cat(id=2, name="Miso", age=2, arrival_date="2026-09-10", status="available"),
        Cat(id=3, name="Luna", age=1, arrival_date="2026-09-15", status="available"),
        Cat(id=4, name="Simba", age=5, arrival_date="2026-09-20", status="available"),
        Cat(id=5, name="Bella", age=8, arrival_date="2026-10-01", status="available"),
        Cat(id=6, name="Oliver", age=3, arrival_date="2026-10-05", status="available"),
        Cat(id=7, name="Milo", age=4, arrival_date="2026-08-01", status="adopted"),
        Cat(id=8, name="Hazel", age=6, arrival_date="2026-09-01", status="foster"),
    ]
    applications = [
        Application(id=101, cat_id=7, stage="finalized", outcome="adopted", stay_days=5),
        Application(id=102, cat_id=2, stage="finalized", outcome="adopted", stay_days=10),
        Application(id=103, cat_id=3, stage="finalized", outcome="adopted", stay_days=15),
        Application(id=104, cat_id=4, stage="finalized", outcome="adopted", stay_days=20),
        Application(id=105, cat_id=5, stage="closed", outcome="withdrawn"),
        Application(id=106, cat_id=1, stage="submitted"),
        Application(id=107, cat_id=6, stage="screening"),
    ]
    return Shelter(cats=cats, applications=applications)


@pytest.fixture
def empty_shelter():
    return Shelter(cats=[], applications=[])


def test_capacity_counts_resident_cats(shelter):
    m = metrics(shelter)
    assert m.cats_in_shelter == 6


def test_average_stay_matches_hand_computed_value(shelter):
    m = metrics(shelter)
    assert m.average_stay_days == 12.5


def test_adoption_rate_uses_closed_outcomes(shelter):
    m = metrics(shelter)
    assert m.adoption_rate == 0.8


def test_longest_waiting_cat_is_the_earliest_arrival(shelter):
    m = metrics(shelter)
    assert m.longest_waiting[0].name == "Pepper"


def test_empty_shelter_returns_zeros(empty_shelter):
    m = metrics(empty_shelter)
    assert m.cats_in_shelter == 0
    assert m.average_stay_days == 0
    assert m.adoption_rate == 0
