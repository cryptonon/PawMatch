"""Unit tests for shelter capacity alerts (risk R-05).

Capacity is 8 places, the seed shelter size. The alert trips at or
over 90 percent full. With a capacity of 8, 7 of 8 is 87.5 percent
and does not trip it; 8 of 8 is 100 percent and does.
"""
from app.metrics.dashboard import CAPACITY, metrics
from app.models import Cat, Shelter


def _shelter_with_residents(count):
    cats = [Cat(id=i + 1, name=f"Cat{i + 1}", age=2, status="available",
                arrival_date="2026-09-01") for i in range(count)]
    return Shelter(cats=cats, applications=[])


def test_no_alert_below_threshold():
    result = metrics(_shelter_with_residents(7))
    assert result.capacity_percent == 87.5
    assert result.alert is None


def test_alert_at_full_capacity():
    result = metrics(_shelter_with_residents(8))
    assert result.capacity_percent == 100.0
    assert result.alert is not None
    assert "90%" in result.alert
    assert "8 of 8" in result.alert


def test_capacity_percent_uses_the_seed_shelter_size():
    assert CAPACITY == 8
    result = metrics(_shelter_with_residents(6))
    assert result.capacity_percent == 75.0
    assert result.alert is None


def test_empty_shelter_has_no_alert():
    result = metrics(Shelter(cats=[], applications=[]))
    assert result.capacity_percent == 0.0
    assert result.alert is None
