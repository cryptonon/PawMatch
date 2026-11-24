"""Shared test fixtures.

The ``freezer`` fixture is provided here with freezegun directly.
pytest-freezegun 0.4.2 cannot be used: it imports ``distutils``, which
was removed in Python 3.12, so it breaks pytest collection entirely.
This fixture gives tests the same ``freezer.move_to(...)`` interface.
"""
import pytest
from freezegun import freeze_time


class _Freezer:
    def __init__(self):
        self._frozen = None

    def move_to(self, target):
        if self._frozen is not None:
            self._frozen.stop()
        self._frozen = freeze_time(target)
        self._frozen.start()

    def stop(self):
        if self._frozen is not None:
            self._frozen.stop()
            self._frozen = None


@pytest.fixture
def freezer():
    frozen = _Freezer()
    yield frozen
    frozen.stop()
