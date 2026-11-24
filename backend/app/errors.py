"""Shared error types. Units re-export these so tests can import the
error from the unit module, for example
``from app.care.timeline import ValidationError``.
"""


class ValidationError(ValueError):
    """Raised when input data fails validation."""


class WorkflowError(ValueError):
    """Raised when a workflow move is not allowed."""
