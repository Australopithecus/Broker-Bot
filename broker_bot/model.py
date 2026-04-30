from __future__ import annotations

import joblib
import pandas as pd
from pathlib import Path
from typing import Any

from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor, VotingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score

from .features import FEATURE_COLUMNS, build_labels


MODEL_FILENAME = "rf_model.joblib"


def _build_model() -> VotingRegressor:
    return VotingRegressor(
        estimators=[
            (
                "random_forest",
                RandomForestRegressor(
                    n_estimators=180,
                    max_depth=6,
                    min_samples_leaf=5,
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
            (
                "extra_trees",
                ExtraTreesRegressor(
                    n_estimators=180,
                    max_depth=7,
                    min_samples_leaf=5,
                    random_state=43,
                    n_jobs=-1,
                ),
            ),
            (
                "hist_gradient_boosting",
                HistGradientBoostingRegressor(
                    max_iter=120,
                    max_leaf_nodes=15,
                    learning_rate=0.04,
                    l2_regularization=0.01,
                    random_state=44,
                ),
            ),
            ("ridge", Ridge(alpha=1.0)),
        ],
    )


def _directional_accuracy(y_true: pd.Series, y_pred: pd.Series) -> float:
    if len(y_true) == 0:
        return 0.0
    return float(((y_true >= 0) == (y_pred >= 0)).mean())


def train_model(features_df: pd.DataFrame, horizon_days: int) -> tuple[Any, dict[str, float]]:
    labels = build_labels(features_df, horizon_days=horizon_days)
    train_df = features_df.dropna(subset=FEATURE_COLUMNS).copy()
    labels = labels.loc[train_df.index]
    valid = labels.notna()
    train_df = train_df.loc[valid]
    labels = labels.loc[valid]
    if train_df.empty:
        raise RuntimeError("Not enough labeled feature rows to train the model.")

    X = train_df[FEATURE_COLUMNS].values
    y = labels.values

    model = _build_model()
    model.fit(X, y)
    preds = pd.Series(model.predict(X), index=labels.index)
    metrics = {
        "r2": float(r2_score(y, preds.values)),
        "mae": float(mean_absolute_error(y, preds.values)),
        "directional_accuracy": _directional_accuracy(labels, preds),
        "model_version": 2.0,
    }
    return model, metrics


def save_model(model: Any, model_dir: str) -> str:
    Path(model_dir).mkdir(parents=True, exist_ok=True)
    path = Path(model_dir) / MODEL_FILENAME
    joblib.dump(model, path)
    return str(path)


def load_model(model_dir: str) -> Any:
    path = Path(model_dir) / MODEL_FILENAME
    if not path.exists():
        raise FileNotFoundError(f"Model file not found: {path}")
    model = joblib.load(path)
    if not hasattr(model, "predict"):
        raise RuntimeError(
            "Saved model does not expose predict(). Please retrain the model with the latest code."
        )
    expected = len(FEATURE_COLUMNS)
    actual = getattr(model, "n_features_in_", None)
    if actual is not None and actual != expected:
        raise RuntimeError(
            f"Model feature mismatch (expected {expected}, found {actual}). "
            "Delete data/models/rf_model.joblib and retrain."
        )
    return model


def predict_return(model: Any, features_df: pd.DataFrame) -> pd.Series:
    X = features_df[FEATURE_COLUMNS].values
    preds = model.predict(X)
    return pd.Series(preds, index=features_df.index, name="pred_return")
