"""Unit tests for the long-stay watchlist (V2)."""
import pytest

from app.matching import stay_risk
from app.models import Cat
from app.seed import sample_cats
from app.watchlist import watchlist


@pytest.fixture
def cats():
    return sample_cats()


def test_watchlist_is_sorted_by_probability_descending(cats):
    entries = watchlist(cats)
    probs = [e.probability for e in entries]
    assert probs == sorted(probs, reverse=True)
    assert all(0.0 <= p <= 1.0 for p in probs)


def test_watchlist_only_lists_available_cats(cats):
    entries = watchlist(cats)
    assert all(e.cat.status == "available" for e in entries)
    assert len(entries) == 6


def test_watchlist_entry_carries_a_reason(cats):
    entries = watchlist(cats)
    for entry in entries:
        assert entry.cat.name in entry.reason
        assert "chance of a long stay" in entry.reason


def test_flagged_cat_appears_first(monkeypatch, cats):
    # Force one cat above the 0.70 flag threshold; the rest keep the
    # real Austin model scores, all below 0.50 for the seed cats.
    real = stay_risk.predict_long_stay

    def patched(cat):
        return 0.82 if cat.name == "Oliver" else real(cat)

    monkeypatch.setattr(stay_risk, "predict_long_stay", patched)
    entries = watchlist(cats)
    assert entries[0].cat.name == "Oliver"
    assert entries[0].flagged is True
    assert entries[0].probability == 0.82
    assert all(e.flagged is False for e in entries[1:])


def test_no_cat_is_flagged_on_the_seed_data(cats):
    entries = watchlist(cats)
    assert all(e.flagged is False for e in entries)
