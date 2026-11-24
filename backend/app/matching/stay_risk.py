"""Unit 6: Stay Risk Prediction (V2).

Predicts the probability that a cat will be a long stay, and flags the
cat for staff attention when the probability reaches the flag threshold
of 0.70. The probability comes from the logistic regression model saved
in model.pkl, trained by train_model.py. Missing behavior notes still
predict, using the documented default (not shy).
"""
import os
import pickle
from dataclasses import dataclass

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
    notes = (cat.behavior_notes or "").lower()
    shy = 1 if "shy" in notes else 0
    age = int(cat.age or 0)
    return [age, shy, 1 if age >= 10 else 0]


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
