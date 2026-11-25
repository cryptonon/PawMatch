"""Unit tests for the Austin training script.

The training data is the Austin analysis table; these tests use a
tiny in-memory frame for the feature builder and a tiny CSV file for
a full train run, so they stay fast. The train run writes its model
to a temporary path, never over the shipped model.pkl.
"""
import pandas as pd

from app.matching import train_model
from app.matching.train_model import austin_features, breed_group, train


def test_breed_group_mapping():
    assert breed_group("Domestic Shorthair Mix") == "DSH"
    assert breed_group("Domestic Longhair") == "Domestic other"
    assert breed_group("Siamese") == "Purebred/mix"


def test_austin_features_use_the_column_order():
    frame = pd.DataFrame({
        "age_days": [365.0, 90.0],
        "is_black_any": [1, 0],
        "intake_type": ["Stray", "Owner Surrender"],
        "cond_group": ["Normal", "Normal"],
        "sex": ["Male", "Female"],
        "kitten_season": [1, 0],
        "occupancy": [629.0, 700.0],
        "breed": ["Domestic Shorthair Mix", "Siamese"],
        "intake_month": [5, 11],
    })
    features = austin_features(frame)
    assert list(features.columns) == train_model.FEATURE_COLUMNS
    assert features.loc[0, "is_kitten"] == 0
    assert features.loc[1, "is_kitten"] == 1
    assert features.loc[0, "is_black_any"] == 1
    assert features.loc[0, "intake_stray"] == 1
    assert features.loc[1, "intake_stray"] == 0


def test_train_on_a_tiny_csv(tmp_path, monkeypatch):
    rows = []
    for i in range(40):
        rows.append({
            "animal_id": f"A{i}", "indt": "2020-01-01", "outdt": "2020-02-01",
            "age_days": 100 + i * 100, "is_black_any": i % 2,
            "intake_type": "Stray" if i % 2 else "Owner Surrender",
            "cond_group": "Normal", "sex": "Female",
            "kitten_season": 0, "occupancy": 600.0,
            "breed": "Domestic Shorthair Mix", "intake_month": 5,
            "long_stay": 1 if i % 3 == 0 else 0,
        })
    path = tmp_path / "tiny.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    monkeypatch.setattr(train_model, "MODEL_PATH", str(tmp_path / "model.pkl"))
    _model, report = train(str(path))
    assert report["rows"] == 40
    assert 0.0 <= report["holdout_auc"] <= 1.0
    assert set(report["coefficients"]) == set(train_model.FEATURE_COLUMNS)
