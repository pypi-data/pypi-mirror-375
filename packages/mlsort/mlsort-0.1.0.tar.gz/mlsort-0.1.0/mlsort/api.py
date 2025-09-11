from __future__ import annotations

import logging
import os
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import numpy as np

from .config import get_artifacts_dir, get_env_bool, get_seed
from .decision import decide
from .installer import load_thresholds, train_thresholds, save_thresholds, Thresholds
from .optimize import gen_cases, optimize_cutoffs
from .algorithms import (
    ALG_TIMSORT, ALG_NP_QUICK, ALG_NP_MERGE, ALG_COUNTING, ALG_RADIX,
    sort_timsort, sort_np, sort_counting, sort_radix_lsd, available_algorithms_for
)


log = logging.getLogger("mlsort")


def _ensure_thresholds(path: str) -> Thresholds:
    # Lazy init: controlled by env flags
    if os.path.exists(path):
        return load_thresholds(path)
    if not get_env_bool("MLSORT_ENABLE_INSTALL_BENCH", False):
        # Safe default if benchmarks disabled
        th = Thresholds(cutoff_n=1024, activation_n=98304, tree={"leaf": True, "label": ALG_NP_QUICK}, feature_names=[
            "n","dtype_code","est_sortedness","est_dup_ratio","est_range","est_entropy","est_run_len"
        ])
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        save_thresholds(path, th)
        return th
    # Run small-budget train+optimize
    seed = get_seed()
    th = train_thresholds(num_samples=600, max_n=120_000, seed=seed, max_depth=3)
    save_thresholds(path, th)
    arrays = gen_cases(num_samples=250, max_n=120_000, seed=seed + 7)
    res = optimize_cutoffs(th, arrays)
    th.cutoff_n = int(res["best"]["cutoff_n"])  # type: ignore[attr-defined]
    th.activation_n = int(res["best"]["activation_n"])  # type: ignore[attr-defined]
    save_thresholds(path, th)
    return th


def select_algorithm(arr: Sequence[Any], thresholds_path: str | None = None, *, key: Any = None, reverse: bool = False) -> str:
    # Input validation
    try:
        n = len(arr)  # type: ignore[arg-type]
    except Exception:
        raise TypeError("arr must be a sequence with __len__ and indexable by int")
    if n == 0:
        return ALG_TIMSORT
    # If a key function is provided, prefer builtin Timsort for correctness and stability
    if key is not None:
        return ALG_TIMSORT
    # If data are strings or mixed/object types, default to Python's Timsort
    try:
        if isinstance(arr, np.ndarray):
            if arr.dtype.kind in {"O", "U", "S"}:
                return ALG_TIMSORT
        else:
            # Sample a subset to determine type categories
            sample_count = min(n, 256)
            idxs = range(sample_count)
            cats = set()
            for i in idxs:
                v = arr[i]
                if isinstance(v, str) or isinstance(v, bytes):
                    cats.add("string")
                elif isinstance(v, (int, float, np.integer, np.floating)):
                    cats.add("number")
                elif v is None:
                    cats.add("other")
                else:
                    # Unknown/object type
                    cats.add("other")
                if len(cats) > 1:
                    break
            if "string" in cats:
                return ALG_TIMSORT
            if len(cats) > 1 or (cats and next(iter(cats)) == "other"):
                return ALG_TIMSORT
    except Exception:
        # On any detection error, prefer safe fallback
        return ALG_TIMSORT
    # Ensure thresholds
    thr_path = thresholds_path or os.path.join(get_artifacts_dir(), "thresholds.json")
    os.makedirs(os.path.dirname(thr_path) or ".", exist_ok=True)
    th = _ensure_thresholds(thr_path)
    algo = decide(arr, th)
    if get_env_bool("MLSORT_DEBUG", False):
        log.debug("mlsort.select algo=%s n=%d path=%s", algo, n, thr_path)
    return algo


def sort(
    arr: Sequence[Any],
    thresholds_path: str | None = None,
    *,
    key: Any = None,
    reverse: bool = False,
) -> List[Any]:
    # Always safe fallback path
    try:
        algo = select_algorithm(arr, thresholds_path, key=key, reverse=reverse)
    except Exception as e:  # strict safety: fallback
        if get_env_bool("MLSORT_DEBUG", False):
            log.debug("mlsort.select failed: %s; falling back to timsort", e)
        algo = ALG_TIMSORT

    # Execute with correct key/reverse handling
    if algo == ALG_TIMSORT:
        a = list(arr)
        a.sort(key=key, reverse=reverse)
        return a

    # For non-Timsort backends, key is unsupported (would have forced Timsort above)
    if algo == ALG_NP_QUICK:
        res = sort_np(arr, kind="quicksort").tolist()
        return res[::-1] if reverse else res
    if algo == ALG_NP_MERGE:
        res = sort_np(arr, kind="mergesort").tolist()
        return res[::-1] if reverse else res
    if algo == ALG_COUNTING:
        try:
            res = sort_counting(arr)
            return res[::-1] if reverse else res
        except Exception:
            res = sort_np(arr, kind="quicksort").tolist()
            return res[::-1] if reverse else res
    if algo == ALG_RADIX:
        try:
            res = sort_radix_lsd(arr)
            return res[::-1] if reverse else res
        except Exception:
            res = sort_np(arr, kind="quicksort").tolist()
            return res[::-1] if reverse else res

    # Last resort: builtin
    a = list(arr)
    a.sort(key=key, reverse=reverse)
    return a


def profile_decisions(samples: int = 100, max_n: int = 200_000, thresholds_path: str | None = None) -> Dict[str, Any]:
    import time
    from .algorithms import time_algorithm
    thr_path = thresholds_path or os.path.join(get_artifacts_dir(), "thresholds.json")
    th = _ensure_thresholds(thr_path)
    arrays = gen_cases(samples, max_n, seed=get_seed()+99)
    rows = []
    for arr in arrays:
        t0 = time.perf_counter()
        algo = decide(arr, th)
        t1 = time.perf_counter()
        t_sort = time_algorithm(arr, algo, repeats=1)
        rows.append({"n": len(arr), "algo": algo, "decision_ms": (t1-t0)*1000.0, "sort_s": t_sort})
    return {"count": len(rows), "rows": rows[:50]}
