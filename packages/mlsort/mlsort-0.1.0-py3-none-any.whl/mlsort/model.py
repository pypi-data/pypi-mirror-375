from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Tuple

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

from .features import to_feature_vector


LABELS = ["timsort", "np_quick", "np_merge", "counting", "radix"]
LABEL_TO_ID = {l: i for i, l in enumerate(LABELS)}
ID_TO_LABEL = {i: l for l, i in LABEL_TO_ID.items()}


@dataclass
class ModelArtifacts:
    model: RandomForestClassifier
    feature_names: List[str]


def make_model(random_state: int = 42) -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_leaf=2,
        random_state=random_state,
        n_jobs=-1,
    )


def fit_model(X: List[List[float]], y: List[str], random_state: int = 42) -> ModelArtifacts:
    y_ids = np.array([LABEL_TO_ID[l] for l in y], dtype=np.int64)
    X_arr = np.asarray(X, dtype=np.float32)
    model = make_model(random_state)
    model.fit(X_arr, y_ids)
    return ModelArtifacts(model=model, feature_names=[
        "n",
        "dtype_code",
        "est_sortedness",
        "est_dup_ratio",
        "est_range",
        "est_entropy",
        "est_run_len",
    ])


def predict(model: RandomForestClassifier, props: Dict[str, float]) -> str:
    X = np.asarray([to_feature_vector(props)], dtype=np.float32)
    y_id = int(model.predict(X)[0])
    return ID_TO_LABEL[y_id]


def load_model(path: str) -> RandomForestClassifier:
    return joblib.load(path)


def save_model(path: str, model: RandomForestClassifier) -> None:
    joblib.dump(model, path)


def predict_best_algo(model: RandomForestClassifier, props: Dict[str, float]) -> str:
    return predict(model, props)


def evaluate_model(model: RandomForestClassifier, X: List[List[float]], y: List[str]) -> Dict:
    y_true = np.array([LABEL_TO_ID[l] for l in y], dtype=np.int64)
    X_arr = np.asarray(X, dtype=np.float32)
    y_pred = model.predict(X_arr)
    acc = accuracy_score(y_true, y_pred)
    all_labels = list(range(len(LABELS)))
    report = classification_report(
        y_true,
        y_pred,
        labels=all_labels,
        target_names=LABELS,
        zero_division=0,
        output_dict=True,
    )
    return {"accuracy": float(acc), "report": report}
