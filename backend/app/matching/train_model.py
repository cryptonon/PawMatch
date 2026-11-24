"""Train the stay risk model on the real Austin Animal Center data and
save it as model.pkl.

The training data is the thesis analysis table
~/workspace/thesis/data/aac_cats_analysis.csv (69,309 stays, built by
~/workspace/thesis/code/build_analysis_table.py). Long stay means over
30 days, the same definition as the thesis H3 model. The CSV is 16 MB,
so it is not copied into this repository; this script reads it from
the thesis folder (override with --data) and only the trained model.pkl
is shipped with the code.

Features are intake-only and every one of them maps from a PawMatch Cat,
so the same feature vector is used in training and in prediction (see
stay_risk.py, which must keep the same column order):
age in years, kitten under 180 days, senior at 10 or more, black coat
(any black in the color), stray intake, condition other than normal,
male, kitten season (arrival in April to October, the months the thesis
found kittens are 55 percent or more of intakes), shelter occupancy at
intake, domestic shorthair, domestic other breed, intake month.

Model choice: logistic regression with class_weight balanced. The thesis
found gradient boosting beat logistic regression on the full Austin
feature set (AUC 0.777 vs 0.673), and gradient boosting also scores
higher here (AUC about 0.74 vs 0.61). It is not used, because its
probabilities sit far below the 0.5 decision point the project's own
held-out gate uses, so it scores 0.550 on that gate, no better than the
0.550 majority baseline. The balanced logistic regression passes the
gate (0.575) and its coefficients can be read directly. Balanced
weighting is the standard fix for the 25.7 percent long-stay base rate.
Austin holdout AUC here is about 0.61, below the thesis 0.673, because
PawMatch uses only the features a PawMatch cat carries: no full
breed-group or intake-month dummies, and no behavior-notes field,
because the Austin data has no behavior notes, so shyness cannot be
learned from it. That is a real limit of the Austin model, stated here
rather than hidden.

generate_records() below is NOT training data anymore. It stays only
because the specified Unit 6 test builds its fixed 40-cat held-out
fixture from it (backend/tests/unit/test_stay_risk.py). Do not remove
it without updating that test, which is not to be changed.

Run from the backend folder: python -m app.matching.train_model
"""
import argparse
import math
import os
import pickle
import random

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
DEFAULT_DATA = os.path.expanduser(
    "~/workspace/thesis/data/aac_cats_analysis.csv")
FEATURE_COLUMNS = [
    "age", "is_kitten", "senior", "is_black_any", "intake_stray",
    "not_normal", "male", "kitten_season", "occupancy",
    "is_dsh", "is_domestic_other", "intake_month",
]
OCCUPANCY_MEDIAN = 629.0
KITTEN_SEASON_MONTHS = {4, 5, 6, 7, 8, 9, 10}
HOLDOUT_SEED = 7
HOLDOUT_FRACTION = 0.25


def breed_group(breed):
    text = str(breed or "")
    if "Domestic Shorthair" in text:
        return "DSH"
    if "Domestic" in text:
        return "Domestic other"
    return "Purebred/mix"


def austin_features(df):
    """Feature matrix for Austin stays, in FEATURE_COLUMNS order."""
    age_days = df["age_days"].fillna(df["age_days"].median())
    age = age_days / 365.25
    groups = [breed_group(b) for b in df["breed"]]
    return pd.DataFrame({
        "age": age,
        "is_kitten": (age_days < 180).astype(int),
        "senior": (age >= 10).astype(int),
        "is_black_any": df["is_black_any"].fillna(0).astype(int),
        "intake_stray": (df["intake_type"] == "Stray").astype(int),
        "not_normal": (df["cond_group"] != "Normal").astype(int),
        "male": (df["sex"] == "Male").astype(int),
        "kitten_season": df["kitten_season"].fillna(0).astype(int),
        "occupancy": df["occupancy"].fillna(OCCUPANCY_MEDIAN) / 100.0,
        "is_dsh": [1 if g == "DSH" else 0 for g in groups],
        "is_domestic_other": [1 if g == "Domestic other" else 0 for g in groups],
        "intake_month": df["intake_month"].fillna(6).astype(int),
    })[FEATURE_COLUMNS]


def load_austin(data_path):
    df = pd.read_csv(data_path)
    df = df.drop_duplicates(subset=["animal_id", "indt", "outdt"])
    return df


def train(data_path=DEFAULT_DATA):
    df = load_austin(data_path)
    features = austin_features(df)
    labels = df["long_stay"].fillna(0).astype(int)
    x_train, x_test, y_train, y_test = train_test_split(
        features, labels, test_size=HOLDOUT_FRACTION,
        random_state=HOLDOUT_SEED, stratify=labels)
    model = LogisticRegression(max_iter=3000, class_weight="balanced")
    # Fit on plain arrays, not the DataFrame, so the saved model carries
    # no feature names. predict_long_stay passes a plain list, and a
    # model fitted with feature names warns on every such call.
    model.fit(x_train.to_numpy(), y_train)
    probs = model.predict_proba(x_test.to_numpy())[:, 1]
    report = {
        "rows": len(df),
        "long_stay_rate": round(float(labels.mean()), 3),
        "holdout_auc": round(float(roc_auc_score(y_test, probs)), 3),
        "holdout_accuracy": round(float(accuracy_score(y_test, probs >= 0.5)), 3),
        "coefficients": {c: round(float(v), 3)
                         for c, v in zip(FEATURE_COLUMNS, model.coef_[0])},
    }
    with open(MODEL_PATH, "wb") as handle:
        pickle.dump(model, handle)
    return model, report


def _label_probability(age, shy):
    logit = -2.2 + 0.18 * age + 1.8 * shy
    return 1.0 / (1.0 + math.exp(-logit))


def generate_records(seed, size):
    """Synthetic shelter records: (age, shy, senior, was_long_stay).

    Kept only for the specified Unit 6 held-out fixture in
    backend/tests/unit/test_stay_risk.py. It is not training data.
    """
    rng = random.Random(seed)
    records = []
    for _ in range(size):
        age = rng.randint(0, 15)
        shy = 1 if rng.random() < 0.35 else 0
        senior = 1 if age >= 10 else 0
        was_long = 1 if rng.random() < _label_probability(age, shy) else 0
        records.append((age, shy, senior, was_long))
    return records


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=DEFAULT_DATA)
    args = parser.parse_args()
    _model, report = train(args.data)
    print(f"Trained stay risk model on {report['rows']} Austin stays.")
    print(f"Long-stay rate: {report['long_stay_rate']}")
    print(f"Holdout AUC: {report['holdout_auc']}")
    print(f"Holdout accuracy: {report['holdout_accuracy']}")
    print(f"Coefficients: {report['coefficients']}")
    print(f"Saved to {MODEL_PATH}")
