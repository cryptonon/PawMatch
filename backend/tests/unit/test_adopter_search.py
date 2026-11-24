"""Unit 4: Adopter Screening and Search. Test code as specified in the unit test report."""
import pytest

from app.adopters.schemas import AdopterProfile
from app.adopters.search import ValidationError, save_profile, search
from app.models import Cat


@pytest.fixture
def cats():
    # 5 cats: 4 available, 1 adopted. Among the 4 available, 2 are good
    # with dogs and 3 are good with children.
    return [
        Cat(id=1, name="Miso", age=2, good_with_dogs=True, good_with_children=True, status="available"),
        Cat(id=2, name="Luna", age=1, good_with_dogs=True, good_with_children=False, status="available"),
        Cat(id=3, name="Simba", age=5, good_with_dogs=False, good_with_children=True, status="available"),
        Cat(id=4, name="Bella", age=8, good_with_dogs=False, good_with_children=True, status="available"),
        Cat(id=5, name="Milo", age=4, good_with_dogs=True, good_with_children=True, status="adopted"),
    ]


def test_adopter_with_dog_excludes_cats_not_good_with_dogs(cats):
    results = search(cats, AdopterProfile(has_dog=True))
    assert all(c.good_with_dogs for c in results)
    assert len(results) == 2


def test_empty_filters_return_all_available_cats(cats):
    results = search(cats, AdopterProfile())
    assert len(results) == 4


def test_adopted_cats_are_not_returned(cats):
    results = search(cats, AdopterProfile())
    assert all(c.status == "available" for c in results)


def test_profile_missing_home_type_is_rejected():
    with pytest.raises(ValidationError):
        save_profile(AdopterProfile(home_type=None, has_dog=False))


def test_good_with_children_filter(cats):
    results = search(cats, AdopterProfile(has_children=True))
    assert all(c.good_with_children for c in results)
    assert len(results) == 3
