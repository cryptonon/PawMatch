"""Unit 5: Compatibility Matching (V2). Test code as specified in the unit test report."""
import pytest

from app.adopters.schemas import AdopterProfile
from app.matching.scoring import rank
from app.models import Cat


@pytest.fixture
def adopter():
    return AdopterProfile(
        has_dog=True, has_children=True,
        preferred_temperament="calm", experience="experienced")


@pytest.fixture
def calm_cat():
    return Cat(id=101, name="Clover", age=3, temperament="calm",
               good_with_dogs=True, good_with_children=True)


@pytest.fixture
def energetic_cat():
    return Cat(id=102, name="Ziggy", age=2, temperament="energetic",
               good_with_dogs=True, good_with_children=True)


@pytest.fixture
def cats():
    # 6 cats. Pepper, the 12 year old senior, fits this adopter best.
    return [
        Cat(id=1, name="Pepper", age=12, temperament="calm",
            good_with_dogs=True, good_with_children=True),
        Cat(id=2, name="Miso", age=2, temperament="calm",
            good_with_dogs=True, good_with_children=True),
        Cat(id=3, name="Luna", age=1, temperament="energetic",
            good_with_dogs=True, good_with_children=False),
        Cat(id=4, name="Simba", age=5, temperament="energetic",
            good_with_dogs=False, good_with_children=True),
        Cat(id=5, name="Bella", age=8, temperament="calm",
            good_with_dogs=False, good_with_children=True),
        Cat(id=6, name="Oliver", age=3, temperament="calm",
            good_with_dogs=True, good_with_children=False),
    ]


@pytest.fixture
def adopters():
    return [
        AdopterProfile(has_dog=True, has_children=True,
                       preferred_temperament="calm", experience="experienced"),
        AdopterProfile(has_dog=False, has_children=False,
                       preferred_temperament="calm", experience="first_time"),
        AdopterProfile(has_dog=True, has_children=False,
                       preferred_temperament="energetic", experience="first_time"),
        AdopterProfile(has_dog=False, has_children=True,
                       preferred_temperament="calm", experience="experienced"),
        AdopterProfile(),
    ]


def test_perfect_fit_scores_highest(adopter, calm_cat, energetic_cat):
    ranked = rank(adopter, [energetic_cat, calm_cat])
    assert ranked[0].cat == calm_cat
    assert ranked[0].score > ranked[1].score


def test_scores_stay_inside_0_to_100(adopters, cats):
    for adopter in adopters:
        for entry in rank(adopter, cats):
            assert 0 <= entry.score <= 100


def test_ranking_is_deterministic(adopter, cats):
    first = [e.cat.id for e in rank(adopter, cats)]
    second = [e.cat.id for e in rank(adopter, cats)]
    assert first == second


def test_matching_senior_cat_is_not_buried(adopter, cats):
    ranked = rank(adopter, cats)
    senior = [e for e in ranked if e.cat.age >= 10][0]
    assert ranked.index(senior) < 3


def test_every_rank_has_a_reason(adopter, cats):
    for entry in rank(adopter, cats):
        assert entry.reason
        assert len(entry.reason) > 10
