from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.tree import DecisionTreeClassifier

from .data import synthesize_dataset
from .model import LABELS, LABEL_TO_ID, ID_TO_LABEL


@dataclass
class Thresholds:
    cutoff_n: int  # use builtin timsort below this
    activation_n: int  # only run ML decision when n >= activation_n; else use a fast default
    tree: Dict[str, Any]
    feature_names: List[str]


FEATURE_NAMES = [
    "n",
    "dtype_code",
    "est_sortedness",
    "est_dup_ratio",
    "est_range",
    "est_entropy",
    "est_run_len",
]


def _train_tree(X: List[List[float]], y: List[str], max_depth: int = 3, random_state: int = 42) -> DecisionTreeClassifier:
    y_ids = np.array([LABEL_TO_ID[l] for l in y], dtype=np.int64)
    X_arr = np.asarray(X, dtype=np.float32)
    tree = DecisionTreeClassifier(max_depth=max_depth, min_samples_leaf=10, random_state=random_state)
    tree.fit(X_arr, y_ids)
    return tree


def _serialize_tree(tree: DecisionTreeClassifier) -> Dict[str, Any]:
    # Convert sklearn tree into a nested dict
    t = tree.tree_
    def node_to_dict(i: int) -> Dict[str, Any]:
        if t.children_left[i] == t.children_right[i]:
            # leaf
            # value shape: (1, n_classes)
            value = t.value[i][0]
            cls_id = int(np.argmax(value))
            return {"leaf": True, "label": ID_TO_LABEL[cls_id]}
        feat_idx = int(t.feature[i])
        thresh = float(t.threshold[i])
        left = int(t.children_left[i])
        right = int(t.children_right[i])
        return {
            "leaf": False,
            "feature_index": feat_idx,
            "threshold": thresh,
            "left": node_to_dict(left),
            "right": node_to_dict(right),
        }
    return node_to_dict(0)


def _estimate_timsort_cutoff(seed: int = 42) -> int:
    # Probe across small sizes and varied distributions and pick the largest n where
    # timsort is best in >= 60% of cases.
    from .algorithms import measure_best_algorithm
    from .data import (
        gen_sorted, gen_reverse, gen_nearly_sorted, gen_uniform, gen_small_range, gen_zipf, gen_normal
    )
    rng = np.random.default_rng(seed)
    sizes = [32, 64, 128, 256, 384, 512, 768, 1024, 1536, 2048]
    gens = [
        lambda n: gen_sorted(n, "int"),
        lambda n: gen_reverse(n, "int"),
        lambda n: gen_nearly_sorted(n, dtype="int"),
        lambda n: gen_uniform(n, "int", 0, 10_000),
        lambda n: gen_uniform(n, "float"),
        lambda n: gen_small_range(n, 128),
        lambda n: gen_zipf(n, a=2.0, dtype="int", max_val=50_000),
        lambda n: gen_normal(n, dtype="float"),
    ]
    cutoff = sizes[0]
    for n in sizes:
        wins = 0
        trials = 0
        for _ in range(12):  # 12 trials per size
            g = gens[rng.integers(0, len(gens))]
            arr = g(n)
            best, _ = measure_best_algorithm(arr, repeats=1)
            if best == "timsort":
                wins += 1
            trials += 1
        frac = wins / max(1, trials)
        if frac >= 0.6:
            cutoff = n
    return int(cutoff)


def _choose_activation_n(cutoff_n: int, max_n: int) -> int:
    # Heuristic: only run ML decision when arrays are "very large".
    # Pick at least 4x cutoff, but not below 32k; cap by max_n.
    base = max(32768, cutoff_n * 4)
    if max_n > 0:
        return int(min(max_n, base))
    return int(base)


def train_thresholds(num_samples: int = 1000, max_n: int = 20000, seed: int = 42, max_depth: int = 3) -> Thresholds:
    samples = synthesize_dataset(num_samples=num_samples, max_n=max_n, seed=seed)
    X = [s.X for s in samples]
    y = [s.y for s in samples]
    tree = _train_tree(X, y, max_depth=max_depth, random_state=seed)
    rules = _serialize_tree(tree)
    cutoff_n = _estimate_timsort_cutoff(seed)
    activation_n = _choose_activation_n(cutoff_n, max_n)
    return Thresholds(cutoff_n=cutoff_n, activation_n=activation_n, tree=rules, feature_names=FEATURE_NAMES)


def save_thresholds(path: str, thresholds: Thresholds) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    data = {
        "cutoff_n": thresholds.cutoff_n,
        "activation_n": thresholds.activation_n,
        "feature_names": thresholds.feature_names,
        "tree": thresholds.tree,
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_thresholds(path: str) -> Thresholds:
    with open(path, "r") as f:
        obj = json.load(f)
    # Backward-compatible: if activation_n missing, derive a conservative default
    activation_n = int(obj.get("activation_n", max(32768, int(obj["cutoff_n"]) * 4)))
    return Thresholds(cutoff_n=int(obj["cutoff_n"]), activation_n=activation_n, tree=obj["tree"], feature_names=list(obj["feature_names"]))
