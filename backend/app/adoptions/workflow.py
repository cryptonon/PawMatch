"""Unit 3: Adoption Workflow.

Moves an adoption application through the fixed stages (submitted,
screening, meet and greet, approved, finalized) and records the outcome.
No stage can be skipped and no application can close without an outcome.
"""
from app.errors import WorkflowError

__all__ = ["WorkflowError", "STAGES", "move", "close"]

STAGES = ["submitted", "screening", "meet_and_greet", "approved", "finalized"]


def move(application, stage, outcome=None):
    """Move an application to the next stage only.

    Raises WorkflowError when the target stage is not the next stage,
    and when finalizing without an outcome. The application is left
    unchanged when the move is blocked.
    """
    if stage not in STAGES:
        raise WorkflowError(f"unknown stage: {stage}")
    current = application.stage
    if current not in STAGES:
        raise WorkflowError(f"application is in stage {current}, which cannot move")
    next_stage = STAGES[STAGES.index(current) + 1] if STAGES.index(current) + 1 < len(STAGES) else None
    if stage != next_stage:
        raise WorkflowError(
            f"cannot move from {current} to {stage}: {next_stage} must come first"
        )
    if stage == "finalized" and outcome is None:
        raise WorkflowError("an outcome is required to finalize an application")
    application.stage = stage
    if outcome is not None:
        application.outcome = outcome
    return application


def close(application, outcome):
    """Close an application early, for example when the adopter withdraws.

    Allowed from any stage before finalized. The outcome is required.
    """
    if application.stage == "finalized":
        raise WorkflowError("a finalized application is already closed")
    if outcome is None:
        raise WorkflowError("an outcome is required to close an application")
    application.stage = "closed"
    application.outcome = outcome
    return application
