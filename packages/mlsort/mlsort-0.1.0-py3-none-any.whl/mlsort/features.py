from __future__ import annotations

import math
import random
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import numpy as np


DTYPE_FLOAT = 0
DTYPE_INT = 1


def infer_dtype(arr: Sequence[Any]) -> int:
    if len(arr) == 0:
        return DTYPE_FLOAT
    # Heuristic: treat as int if all elements are ints or can be safely cast to ints
    if all(isinstance(x, (int, np.integer)) for x in arr):
        return DTYPE_INT
    if isinstance(arr, np.ndarray) and np.issubdtype(arr.dtype, np.integer):
        return DTYPE_INT
    return DTYPE_FLOAT


def _sample_indices(n: int, k: int) -> List[int]:
    if n <= 1 or k <= 0:
        return []
    k = min(k, n - 1)
    # Use fixed-seed RNG per call? We'll let caller set global seed.
    return random.sample(range(n - 1), k)


def est_sortedness(arr: Sequence[Any], sample: int = 256) -> float:
    n = len(arr)
    if n < 2:
        return 1.0
    idxs = _sample_indices(n, min(sample, n - 1))
    if not idxs:
        return 1.0
    good = 0
    for i in idxs:
        try:
            if arr[i] <= arr[i + 1]:
                good += 1
        except Exception:
            # Fallback: consider incomparable as unsorted
            pass
    return good / len(idxs)


def est_duplicate_ratio(arr: Sequence[Any], sample: int = 256) -> float:
    if len(arr) == 0:
        return 0.0
    if sample > len(arr):
        sample = len(arr)
    idxs = random.sample(range(len(arr)), sample)
    vals = [arr[i] for i in idxs]
    uniq = len(set(vals))
    dup_ratio = 1.0 - (uniq / sample if sample > 0 else 1.0)
    return dup_ratio


def est_range(arr: Sequence[Any], sample: int = 256) -> float:
    if len(arr) == 0:
        return 0.0
    if sample > len(arr):
        sample = len(arr)
    idxs = random.sample(range(len(arr)), sample)
    vals = [arr[i] for i in idxs]
    try:
        vmin = min(vals)
        vmax = max(vals)
        return float(vmax) - float(vmin)
    except Exception:
        return 0.0


def est_entropy(arr: Sequence[Any], bins: int = 32, sample: int = 512) -> float:
    if len(arr) == 0:
        return 0.0
    if sample > len(arr):
        sample = len(arr)
    idxs = random.sample(range(len(arr)), sample)
    vals = np.asarray([arr[i] for i in idxs])
    if np.issubdtype(vals.dtype, np.integer):
        vmin = int(vals.min())
        vmax = int(vals.max())
        if vmax == vmin:
            return 0.0
        # For ints, clamp number of bins to observed range
        rng = vmax - vmin + 1
        bins_ = min(bins, rng)
        hist, _ = np.histogram(vals, bins=bins_, range=(vmin, vmax + 1))
    else:
        vmin = float(np.min(vals))
        vmax = float(np.max(vals))
        if vmax == vmin:
            return 0.0
        hist, _ = np.histogram(vals, bins=bins, range=(vmin, vmax))
    p = hist.astype(np.float64)
    p_sum = p.sum()
    if p_sum == 0:
        return 0.0
    p = p / p_sum
    # Shannon entropy
    ent = -np.sum(p[p > 0] * np.log2(p[p > 0]))
    # Normalize by max entropy (log2 of number of non-empty bins)
    nonzero_bins = max(1, (p > 0).sum())
    max_ent = math.log2(nonzero_bins)
    return float(ent / max_ent) if max_ent > 0 else 0.0


def est_run_length(arr: Sequence[Any], sample_windows: int = 16, window_size: int = 128) -> float:
    n = len(arr)
    if n == 0:
        return 0.0
    if n <= 1:
        return float(n)
    windows = []
    for _ in range(min(sample_windows, max(1, n // max(1, window_size)))):
        start = random.randint(0, max(0, n - window_size)) if n > window_size else 0
        end = min(n, start + window_size)
        windows.append((start, end))
    runs_total = 0
    elems_total = 0
    for s, e in windows:
        if e - s <= 1:
            runs_total += (e - s)
            elems_total += (e - s)
            continue
        prev = arr[s]
        direction = 0  # 1 increasing, -1 decreasing, 0 unknown
        runs = 1
        for i in range(s + 1, e):
            curr = arr[i]
            # Avoid numpy boolean arithmetic; use explicit branching
            if curr > prev:
                curr_dir = 1
            elif curr < prev:
                curr_dir = -1
            else:
                curr_dir = direction  # equal values extend the current run
            if curr_dir != direction and direction != 0:
                runs += 1
            direction = curr_dir if direction != 0 else curr_dir or 0
            prev = curr
        runs_total += runs
        elems_total += (e - s)
    avg_run_len = (elems_total / runs_total) if runs_total > 0 else float(n)
    return float(avg_run_len)


def estimate_properties(arr: Sequence[Any]) -> Dict[str, float]:
    n = len(arr)
    dtype_code = infer_dtype(arr)
    props = {
        "n": float(n),
        "dtype_code": float(dtype_code),
        "est_sortedness": est_sortedness(arr),
        "est_dup_ratio": est_duplicate_ratio(arr),
        "est_range": est_range(arr),
        "est_entropy": est_entropy(arr),
        "est_run_len": est_run_length(arr),
    }
    return props


def to_feature_vector(props: Dict[str, float]) -> List[float]:
    keys = [
        "n",
        "dtype_code",
        "est_sortedness",
        "est_dup_ratio",
        "est_range",
        "est_entropy",
        "est_run_len",
    ]
    return [float(props[k]) for k in keys]
