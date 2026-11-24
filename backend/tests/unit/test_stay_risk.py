"""Unit 6: Stay Risk Prediction (V2). Test code as specified in the unit test report."""
from statistics import mean

import pytest

from app.matching import stay_risk
from app.matching.stay_risk import assess, predict_long_stay
from app.matching.train_model import generate_records
from app.models import Cat
from app.seed import sample_cats


@pytest.fixture
def cats():
    return sample_cats()


@pytest.fixture
def cat():
    return Cat(id=1, name="Miso", age=2, behavior_notes="Friendly and playful")


@pytest.fixture
def held_out():
    # Fixed held out fixture of 40 historical cats with known outcomes,
    # generated from the same shelter pattern as the training data but
    # with a different seed, so none of them were used in training.
    records = generate_records(20261025, 40)
    cats = []
    for index, (age, shy, _senior, was_long) in enumerate(records):
        notes = "Shy with visitors" if shy else "Friendly and confident"
        cats.append(Cat(id=500 + index, name=f"Hist{index}", age=age,
                        behavior_notes=notes, was_long_stay=bool(was_long)))
    return cats


def test_probability_is_inside_0_to_1(cats):
    for cat in cats:
        p = predict_long_stay(cat)
        assert 0.0 <= p <= 1.0


def test_flag_is_set_at_the_threshold(monkeypatch, cat):
    monkeypatch.setattr(stay_risk, "predict_long_stay", lambda c: 0.70)
    assert assess(cat).flagged is True
    monkeypatch.setattr(stay_risk, "predict_long_stay", lambda c: 0.69)
    assert assess(cat).flagged is False


def test_missing_behavior_notes_still_predicts(cat):
    cat.behavior_notes = None
    result = assess(cat)
    assert result.probability is not None


def test_model_beats_baseline_on_held_out_fixture(held_out):
    correct = sum(1 for c in held_out if (predict_long_stay(c) >= 0.5) == c.was_long_stay)
    accuracy = correct / len(held_out)
    baseline = max(mean(c.was_long_stay for c in held_out), 1 - mean(c.was_long_stay for c in held_out))
    assert accuracy > baseline
