"""Unit 5: Compatibility Matching (V2).

Scores how well each available cat fits an adopter profile, ranks the
cats by that score, and returns a plain language reason for every rank.

The rules are visible and deterministic:
- temperament match: 40 points when the cat temperament is the one the
  adopter asked for.
- good with dogs: 15 points when the adopter has a dog and the cat is
  good with dogs.
- good with children: 15 points when the adopter has children and the
  cat is good with children.
- experience: 15 points for a senior cat (age 10 or more) with an
  experienced adopter, 5 points for a cat aged 7 or more with an
  experienced adopter. Age is never a penalty, so a senior cat that
  fits best is never buried for its age.
Scores are clamped to 0 to 100. Ties break by cat id, so the same input
always gives the same ranking.
"""
from dataclasses import dataclass

from app.adopters.search import search as filtered_search


@dataclass
class RankEntry:
    cat: object
    score: int
    reason: str


def _score(adopter, cat):
    points = 0
    reasons = []
    preferred = getattr(adopter, "preferred_temperament", None)
    if preferred and cat.temperament == preferred:
        points += 40
        reasons.append(f"a {cat.temperament} cat, which is what you asked for")
    if adopter.has_dog and cat.good_with_dogs:
        points += 15
        reasons.append("good with dogs")
    if adopter.has_children and cat.good_with_children:
        points += 15
        reasons.append("good with children")
    if getattr(adopter, "experience", None) == "experienced":
        if cat.age >= 10:
            points += 15
            reasons.append("a senior cat that fits an experienced home")
        elif cat.age >= 7:
            points += 5
            reasons.append("an older cat that fits an experienced home")
    if reasons:
        reason = f"{cat.name} is " + " and ".join(reasons) + "."
    else:
        reason = (
            f"{cat.name} is a {cat.temperament} cat; a lively companion "
            "that needs an active home."
        )
    return max(0, min(100, points)), reason


def rank(adopter, cats):
    """Rank the available cats that fit the adopter profile.

    The adopter filters (dog, children, available only) apply first, so
    a ranked cat always passes the V1 filtered search. Entries are
    sorted by score, ties by cat id.
    """
    fitting = filtered_search(cats, adopter)
    entries = []
    for cat in fitting:
        score, reason = _score(adopter, cat)
        entries.append(RankEntry(cat=cat, score=score, reason=reason))
    entries.sort(key=lambda e: (-e.score, e.cat.id))
    return entries
