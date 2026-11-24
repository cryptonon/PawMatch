"""Unit 1: Intake Validation. Test code as specified in the unit test report."""
from app.intake.validation import validate_intake


def valid_form(**overrides):
    form = {
        "name": "Miso",
        "age": 2,
        "breed": "Domestic Shorthair",
        "sex": "F",
        "arrival_date": "2026-10-01",
        "source": "stray",
        "health_status": "healthy",
        "behavior_notes": "Calm, likes laps.",
    }
    form.update(overrides)
    return form


def test_complete_form_is_accepted():
    result = validate_intake(valid_form())
    assert result.ok is True
    assert result.errors == []


def test_missing_age_is_rejected():
    form = valid_form()
    del form["age"]
    result = validate_intake(form)
    assert result.ok is False
    assert "age" in result.errors


def test_negative_age_is_rejected():
    result = validate_intake(valid_form(age=-1))
    assert result.ok is False
    assert "age" in result.errors


def test_age_above_maximum_is_rejected():
    result = validate_intake(valid_form(age=31))
    assert result.ok is False
    assert "age" in result.errors


def test_boundary_ages_are_accepted():
    assert validate_intake(valid_form(age=0)).ok is True
    assert validate_intake(valid_form(age=30)).ok is True


def test_future_arrival_date_is_rejected():
    result = validate_intake(valid_form(arrival_date="2999-01-01"))
    assert result.ok is False
    assert "arrival_date" in result.errors
