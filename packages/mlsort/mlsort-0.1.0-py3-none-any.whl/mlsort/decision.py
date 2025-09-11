from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from .features import estimate_properties, to_feature_vector
from .algorithms import ALG_TIMSORT, ALG_NP_QUICK, ALG_NP_MERGE, ALG_COUNTING, ALG_RADIX, available_algorithms_for


def _eval_tree(tree: Dict[str, Any], feature_names: List[str], X: List[float]) -> str:
    node = tree
    while not node.get("leaf", False):
        idx = int(node["feature_index"])
        thr = float(node["threshold"])
        if X[idx] <= thr:
            node = node["left"]
        else:
            node = node["right"]
    return str(node["label"])


def decide(arr, thresholds) -> str:
    # 1) Size cutoffs
    n = len(arr)
    if n < thresholds.cutoff_n:
        return ALG_TIMSORT
    # For arrays between cutoff and activation, use a fast default (np_quick)
    if n < getattr(thresholds, "activation_n", thresholds.cutoff_n * 4):
        return ALG_NP_QUICK

    # 2) Estimate features only for very large arrays
    props = estimate_properties(arr)
    X = to_feature_vector(props)

    # 3) Evaluate decision tree
    label = _eval_tree(thresholds.tree, thresholds.feature_names, X)

    # 4) Respect algorithm availability for dtype/range; fallback if needed
    algos = set(available_algorithms_for(arr))
    if label in algos:
        return label
    # fallback preference order depending on dtype
    if ALG_NP_QUICK in algos:
        return ALG_NP_QUICK
    if ALG_NP_MERGE in algos:
        return ALG_NP_MERGE
    return ALG_TIMSORT
