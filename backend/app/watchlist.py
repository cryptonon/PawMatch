"""Long-stay watchlist for staff (V2).

Lists the available cats assessed by the stay-risk model, highest
probability first, with the probability, whether the cat is flagged
at the 0.70 threshold, and a plain-language reason. The reason names
the factors behind the score, in the words of the Austin data: kittens
and kitten-season arrivals wait longer, black cats wait longer, and
among adults the wait grows with age.
"""
from dataclasses import dataclass

from app.matching import stay_risk


@dataclass
class WatchlistEntry:
    cat: object
    probability: float
    flagged: bool
    reason: str


def _reason(cat, probability):
    age = int(cat.age or 0)
    parts = []
    if age * 365.25 < 180:
        parts.append("arrived as a kitten")
    if "black" in (cat.color or "").lower():
        parts.append("black cats wait longer in the Austin data")
    if age >= 10:
        parts.append("senior cats wait longer")
    month = int(str(cat.arrival_date or "2026-01-01").split("-")[1])
    if month in {4, 5, 6, 7, 8, 9, 10}:
        parts.append("arrived in kitten season")
    if not parts:
        parts.append("age and intake history")
    joined = "; ".join(parts)
    return (f"{cat.name} has a {probability:.0%} chance of a long stay "
            f"({joined}).")


def watchlist(cats):
    """Available cats only, highest probability first."""
    entries = []
    for cat in cats:
        if cat.status != "available":
            continue
        assessment = stay_risk.assess(cat)
        # Round once, here, so the reason, the flag, and the number the
        # API returns all describe the same probability. Rounding later
        # in the API made Miso read 38% in the score and 37% in the
        # reason for the same 0.3748 probability.
        probability = round(assessment.probability, 3)
        entries.append(WatchlistEntry(
            cat=cat,
            probability=probability,
            flagged=probability >= stay_risk.THRESHOLD,
            reason=_reason(cat, probability),
        ))
    entries.sort(key=lambda e: e.probability, reverse=True)
    return entries
