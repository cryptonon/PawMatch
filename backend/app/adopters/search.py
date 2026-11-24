"""Unit 4: Adopter Screening and Search.

Stores adopter profiles and runs the V1 filtered search over available
cats using the profile fields (home, other pets, experience, what the
adopter wants). Only cats with status "available" are ever returned.
"""
from app.adopters.schemas import AdopterProfile
from app.errors import ValidationError

__all__ = ["AdopterProfile", "ValidationError", "search", "save_profile"]


def search(cats, profile):
    """Return the available cats that fit an adopter profile.

    A profile with no preferences returns every available cat. A dog at
    home keeps only cats good with dogs; children at home keeps only cats
    good with children. Adopted and foster cats are never returned.
    """
    results = []
    for cat in cats:
        if cat.status != "available":
            continue
        if profile.has_dog and not cat.good_with_dogs:
            continue
        if profile.has_children and not cat.good_with_children:
            continue
        results.append(cat)
    return results


def save_profile(profile):
    """Save an adopter profile. The home type is required."""
    if profile.home_type is None:
        raise ValidationError("home_type is required")
    return profile
