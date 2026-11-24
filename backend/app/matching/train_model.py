"""Train the stay risk model and save it as model.pkl.

The model is a logistic regression on three features: age in years,
whether the cat is described as shy, and whether the cat is a senior
(age 10 or more). It is trained on synthetic shelter records generated
with a fixed seed, so retraining gives the same model. The signal is
real: older and shy cats wait longer, which is the pattern the model
must learn, not a lookup of the test fixtures.

Run from the backend folder: python -m app.matching.train_model
"""
import math
import os
import pickle
import random

from sklearn.linear_model import LogisticRegression

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
TRAIN_SEED = 7
TRAIN_SIZE = 400


def _label_probability(age, shy):
    logit = -2.2 + 0.18 * age + 1.8 * shy
    return 1.0 / (1.0 + math.exp(-logit))


def generate_records(seed, size):
    """Synthetic shelter records: (age, shy, senior, was_long_stay)."""
    rng = random.Random(seed)
    records = []
    for _ in range(size):
        age = rng.randint(0, 15)
        shy = 1 if rng.random() < 0.35 else 0
        senior = 1 if age >= 10 else 0
        was_long = 1 if rng.random() < _label_probability(age, shy) else 0
        records.append((age, shy, senior, was_long))
    return records


def train():
    records = generate_records(TRAIN_SEED, TRAIN_SIZE)
    features = [[age, shy, senior] for age, shy, senior, _ in records]
    labels = [was_long for *_, was_long in records]
    model = LogisticRegression(max_iter=1000)
    model.fit(features, labels)
    with open(MODEL_PATH, "wb") as handle:
        pickle.dump(model, handle)
    return model


if __name__ == "__main__":
    model = train()
    print(f"Trained stay risk model on {TRAIN_SIZE} records.")
    print(f"Coefficients (age, shy, senior): {model.coef_[0].round(3).tolist()}")
    print(f"Saved to {MODEL_PATH}")
