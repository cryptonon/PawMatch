"""Unit 1: Intake Validation.

Validates a cat intake form before a profile is created. Every required
field must be present and every value must be inside its allowed range,
so no bad record enters the system.
"""
import datetime as _dt
from dataclasses import dataclass, field

REQUIRED_FIELDS = ["name", "age", "breed", "sex", "arrival_date", "source"]
MIN_AGE = 0
MAX_AGE = 30


@dataclass
class ValidationResult:
    ok: bool
    errors: list = field(default_factory=list)


def validate_intake(form):
    """Validate an intake form given as a dict.

    Returns a ValidationResult with ok True and an empty error list when
    the form is valid. Otherwise ok is False and errors names the fields
    that failed, using the field names from the form.
    """
    errors = []
    for name in REQUIRED_FIELDS:
        value = form.get(name)
        if value is None or (isinstance(value, str) and value.strip() == ""):
            errors.append(name)

    age = form.get("age")
    if age is not None and "age" not in errors:
        if isinstance(age, bool) or not isinstance(age, int) or age < MIN_AGE or age > MAX_AGE:
            errors.append("age")

    arrival = form.get("arrival_date")
    if arrival is not None and "arrival_date" not in errors:
        try:
            arrival_date = _dt.date.fromisoformat(str(arrival))
        except ValueError:
            errors.append("arrival_date")
        else:
            if arrival_date > _dt.date.today():
                errors.append("arrival_date")

    return ValidationResult(ok=not errors, errors=errors)
