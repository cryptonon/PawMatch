"""Unit tests for AI-drafted adoption bios (V2).

Drafting is rule-based from the cat profile and staff notes (no
external AI API in this project). The workflow is the point: a draft
is created, staff approve it, and only an approved bio can publish.
"""
import pytest

from app.bios.drafting import (
    BioError, approve, create_draft, draft_bio, get_bio, publish)
from app.models import Cat


@pytest.fixture(autouse=True)
def clear():
    from app.bios import drafting
    drafting.clear_store()
    yield
    drafting.clear_store()


def test_draft_names_the_cat_and_its_temperament():
    cat = Cat(id=1, name="Pepper", age=12, breed="Domestic Shorthair",
              temperament="calm", good_with_dogs=True,
              good_with_children=True,
              behavior_notes="Calm and shy with visitors")
    text = draft_bio(cat)
    assert "Pepper" in text
    assert "calm" in text.lower()
    assert "12 years old" in text
    assert "good with dogs" in text.lower()
    assert "Calm and shy with visitors" in text


def test_draft_for_a_kitten_says_kitten():
    cat = Cat(id=2, name="Luna", age=0, breed="Tabby",
              temperament="energetic", good_with_dogs=False,
              good_with_children=False, behavior_notes="Energetic")
    assert "young kitten" in draft_bio(cat)


def test_senior_cat_draft_mentions_a_calm_home():
    cat = Cat(id=3, name="Pepper", age=12, breed="Domestic Shorthair",
              temperament="calm", behavior_notes="")
    assert "calm home" in draft_bio(cat)


def test_approve_moves_a_draft_to_approved():
    cat = Cat(id=1, name="Miso", age=2, temperament="calm")
    create_draft(cat)
    assert get_bio(1).state == "draft"
    assert approve(1).state == "approved"


def test_publish_a_draft_is_rejected():
    cat = Cat(id=1, name="Miso", age=2, temperament="calm")
    create_draft(cat)
    with pytest.raises(BioError):
        publish(1)
    assert get_bio(1).state == "draft"


def test_publish_an_approved_bio_works():
    cat = Cat(id=1, name="Miso", age=2, temperament="calm")
    create_draft(cat)
    approve(1)
    assert publish(1).state == "published"


def test_new_draft_after_publishing_returns_to_draft():
    cat = Cat(id=1, name="Miso", age=2, temperament="calm")
    create_draft(cat)
    approve(1)
    publish(1)
    assert create_draft(cat).state == "draft"
