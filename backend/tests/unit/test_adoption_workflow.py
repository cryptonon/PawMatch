"""Unit 3: Adoption Workflow. Test code as specified in the unit test report."""
import pytest

from app.adoptions.workflow import WorkflowError, close, move
from app.models import Application


@pytest.fixture
def application():
    return Application(id=201, cat_id=1, adopter_name="Test Adopter")


def test_each_valid_transition_is_allowed(application):
    move(application, "screening")
    move(application, "meet_and_greet")
    move(application, "approved")
    move(application, "finalized", outcome="adopted")
    assert application.stage == "finalized"
    assert application.outcome == "adopted"


def test_skipping_stages_is_blocked(application):
    with pytest.raises(WorkflowError):
        move(application, "finalized", outcome="adopted")


def test_finalize_before_meet_and_greet_is_blocked(application):
    move(application, "screening")
    with pytest.raises(WorkflowError):
        move(application, "finalized", outcome="adopted")


def test_closing_without_outcome_is_blocked(application):
    move(application, "screening")
    move(application, "meet_and_greet")
    move(application, "approved")
    with pytest.raises(WorkflowError):
        move(application, "finalized", outcome=None)


def test_withdrawn_outcome_is_recorded(application):
    move(application, "screening")
    close(application, outcome="withdrawn")
    assert application.outcome == "withdrawn"
