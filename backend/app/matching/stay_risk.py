"""Unit 6: Stay Risk Prediction (V2).

Predicts the probability that a cat will be a long stay, and flags the
cat for staff attention when the probability reaches the flag threshold
of 0.70. The probability comes from the logistic regression model saved
in model.pkl, trained on the real Austin Animal Center data by
train_model.py (69,309 stays, long stay over 30 days). The feature
vector below must keep the same column order as train_model.py.

Mapping from a PawMatch Cat: age in years, kitten under 180 days,
senior at 10 or more, black coat from the color field, stray intake
from the source field (the source is the intake type), condition other
than normal from the health status, male from the sex field, kitten
season from the arrival month, domestic shorthair or domestic other
from the breed. The Austin data has no shelter census for a PawMatch
cat, so occupancy uses the Austin median (629). The Austin data also
has no behavior notes, so shyness is not a model input: a shy cat is
scored on its age, coat, and intake like any other cat. That is a
limit of training on Austin, not a bug in this unit.

Missing behavior notes still predict, because the model never reads
them; assess() only needs the cat fields above.
"""
import os
import pickle
from dataclasses import dataclass

from app.matching.train_model import (
    FEATURE_COLUMNS, KITTEN_SEASON_MONTHS, OCCUPANCY_MEDIAN, breed_group)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
THRESHOLD = 0.70

_MODEL = None


@dataclass
class Assessment:
    probability: float
    flagged: bool


def _load_model():
    global _MODEL
    if _MODEL is None:
        with open(MODEL_PATH, "rb") as handle:
            _MODEL = pickle.load(handle)
    return _MODEL


def _features(cat):
    age = int(cat.age or 0)
    age_days = age * 365.25
    month = int(str(cat.arrival_date or "2026-01-01").split("-")[1])
    group = breed_group(cat.breed)
    values = {
        "age": float(age),
        "is_kitten": 1 if age_days < 180 else 0,
        "senior": 1 if age >= 10 else 0,
        "is_black_any": 1 if "black" in (cat.color or "").lower() else 0,
        "intake_stray": 1 if (cat.source or "").lower() == "stray" else 0,
        "not_normal": 0 if (cat.health_status or "healthy").lower() == "healthy" else 1,
        "male": 1 if cat.sex == "M" else 0,
        "kitten_season": 1 if month in KITTEN_SEASON_MONTHS else 0,
        "occupancy": OCCUPANCY_MEDIAN / 100.0,
        "is_dsh": 1 if group == "DSH" else 0,
        "is_domestic_other": 1 if group == "Domestic other" else 0,
        "intake_month": month,
    }
    return [values[name] for name in FEATURE_COLUMNS]


def predict_long_stay(cat):
    """Probability (0.0 to 1.0) that this cat will be a long stay."""
    model = _load_model()
    if model is None:
        raise RuntimeError("stay risk model is offline")
    return float(model.predict_proba([_features(cat)])[0][1])


def assess(cat):
    """Assess one cat: its probability and whether it is flagged.

    The threshold is inclusive: 0.70 flags the cat, 0.69 does not.
    """
    probability = predict_long_stay(cat)
    return Assessment(probability=probability, flagged=probability >= THRESHOLD)
