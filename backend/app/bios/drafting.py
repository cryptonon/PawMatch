"""AI-drafted adoption bios (V2).

The proposal calls for bios drafted from staff notes by an AI API,
with staff approval before anything is published. There is no external
AI API and no API key in this project, so the drafting here is
rule-based: fixed sentence patterns filled from the cat profile and
the staff notes. The workflow is the part that matters for the
assignment, and it is the same either way: a draft is created, staff
approve it, and only an approved bio can be published. Nothing reaches
an adopter without staff approval.

States: draft -> approved -> published. Publishing a draft is
rejected with a BioError. Approving a published bio is a no-op.
Creating a new draft replaces the current one and returns it to draft.
"""
from dataclasses import dataclass


class BioError(Exception):
    """Raised when a bio workflow step is not allowed in its state."""


@dataclass
class Bio:
    cat_id: int
    text: str
    state: str  # draft, approved, published


_DRAFTS = {}


def draft_bio(cat, notes=None):
    """Draft a short bio from the cat profile and staff notes."""
    staff_notes = (notes or cat.behavior_notes or "").strip()
    age = int(cat.age or 0)
    if age == 0:
        age_text = "a young kitten"
    elif age == 1:
        age_text = "1 year old"
    elif age >= 10:
        age_text = f"{age} years old and looking for a calm home"
    else:
        age_text = f"{age} years old"
    parts = [f"Meet {cat.name}, {age_text} {cat.breed}."]
    if (cat.temperament or "").lower() == "calm":
        parts.append(f"{cat.name} is a calm cat who likes quiet rooms.")
    elif (cat.temperament or "").lower() == "energetic":
        parts.append(f"{cat.name} is an energetic cat who loves to play.")
    if cat.good_with_dogs:
        parts.append(f"{cat.name} is good with dogs.")
    if cat.good_with_children:
        parts.append(f"{cat.name} is good with children.")
    if staff_notes:
        parts.append(f"Staff notes: {staff_notes}")
    return " ".join(parts)


def create_draft(cat, notes=None):
    bio = Bio(cat_id=cat.id, text=draft_bio(cat, notes), state="draft")
    _DRAFTS[cat.id] = bio
    return bio


def get_bio(cat_id):
    return _DRAFTS.get(cat_id)


def approve(cat_id):
    bio = _DRAFTS.get(cat_id)
    if bio is None:
        raise BioError("no bio draft for this cat")
    if bio.state == "published":
        return bio
    bio.state = "approved"
    return bio


def publish(cat_id):
    bio = _DRAFTS.get(cat_id)
    if bio is None:
        raise BioError("no bio draft for this cat")
    if bio.state != "approved":
        raise BioError("only an approved bio can be published")
    bio.state = "published"
    return bio


def clear_store():
    _DRAFTS.clear()
