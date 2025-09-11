from __future__ import annotations

import math
import time
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np


ALG_TIMSORT = "timsort"
ALG_NP_QUICK = "np_quick"
ALG_NP_MERGE = "np_merge"
ALG_COUNTING = "counting"
ALG_RADIX = "radix"

ALL_ALGOS = [ALG_TIMSORT, ALG_NP_QUICK, ALG_NP_MERGE, ALG_COUNTING, ALG_RADIX]


def _as_numpy(arr: Sequence[Any]) -> np.ndarray:
    if isinstance(arr, np.ndarray):
        return arr
    return np.asarray(arr)


def _as_list(arr: Sequence[Any]) -> List[Any]:
    if isinstance(arr, list):
        return list(arr)
    return list(arr)


def sort_timsort(arr: Sequence[Any]) -> List[Any]:
    a = _as_list(arr)
    a.sort()
    return a


def sort_np(arr: Sequence[Any], kind: str) -> np.ndarray:
    a = _as_numpy(arr)
    return np.sort(a, kind=kind)


def sort_counting(arr: Sequence[int]) -> List[int]:
    a = _as_numpy(arr)
    if not np.issubdtype(a.dtype, np.integer):
        raise TypeError("counting sort requires integer dtype")
    if a.size == 0:
        return []
    amin = int(a.min())
    amax = int(a.max())
    rng = amax - amin + 1
    # Safety cap: avoid huge memory
    if rng > 1_000_000:
        raise ValueError("range too large for counting sort")
    counts = np.zeros(rng, dtype=np.int64)
    # Shift values to zero-based
    shifted = (a - amin).astype(np.int64)
    for v in shifted:
        counts[v] += 1
    # Build output
    out = np.empty_like(shifted)
    total = 0
    for i in range(rng):
        c = int(counts[i])
        if c:
            out[total: total + c] = i
            total += c
    # Shift back
    out = (out + amin).astype(a.dtype, copy=False)
    return out.tolist()


def sort_radix_lsd(arr: Sequence[int], base: int = 256) -> List[int]:
    a = _as_numpy(arr)
    if not np.issubdtype(a.dtype, np.integer):
        raise TypeError("radix sort requires integer dtype")
    if a.size == 0:
        return []
    # Use 32-bit buckets for speed; bias signed to unsigned
    dtype = a.dtype
    bits = np.iinfo(dtype).bits
    bias = 1 << (bits - 1)
    u = (a.astype(np.int64) + bias).astype(np.uint64)
    out = u.copy()
    mask = base - 1
    shift = 0
    tmp = np.empty_like(out)
    while shift < bits:
        counts = np.zeros(base, dtype=np.int64)
        # Count
        for v in out:
            counts[(v >> shift) & mask] += 1
        # Prefix sums
        total = 0
        for i in range(base):
            c = counts[i]
            counts[i] = total
            total += c
        # Reorder
        for v in out:
            b = (v >> shift) & mask
            tmp[counts[b]] = v
            counts[b] += 1
        out, tmp = tmp, out
        shift += int(math.log2(base))
    # Un-bias
    res = (out.astype(np.int64) - bias).astype(dtype, copy=False)
    return res.tolist()


def available_algorithms_for(arr: Sequence[Any]) -> List[str]:
    a = _as_numpy(arr)
    algos = [ALG_TIMSORT, ALG_NP_QUICK, ALG_NP_MERGE]
    if np.issubdtype(a.dtype, np.integer):
        # counting only if range manageable
        if a.size > 0:
            amin = int(a.min())
            amax = int(a.max())
            rng = amax - amin + 1
            if rng <= 100_000 and rng <= 8 * a.size:
                algos.append(ALG_COUNTING)
        algos.append(ALG_RADIX)
    return algos


def time_algorithm(arr: Sequence[Any], algo: str, repeats: int = 1) -> float:
    start = time.perf_counter
    best = float("inf")
    for _ in range(repeats):
        t0 = start()
        if algo == ALG_TIMSORT:
            sort_timsort(arr)
        elif algo == ALG_NP_QUICK:
            sort_np(arr, kind="quicksort")
        elif algo == ALG_NP_MERGE:
            sort_np(arr, kind="mergesort")
        elif algo == ALG_COUNTING:
            sort_counting(arr)
        elif algo == ALG_RADIX:
            sort_radix_lsd(arr)
        else:
            raise ValueError(f"unknown algo {algo}")
        best = min(best, start() - t0)
    return best


def measure_best_algorithm(arr: Sequence[Any], repeats: int = 1):
    algos = available_algorithms_for(arr)
    times: Dict[str, float] = {}
    for algo in algos:
        try:
            t = time_algorithm(arr, algo, repeats=repeats)
            times[algo] = t
        except Exception:
            # skip invalid
            continue
    if not times:
        # fallback
        return ALG_TIMSORT, {ALG_TIMSORT: float("inf")}
    best_algo = min(times.items(), key=lambda kv: kv[1])[0]
    return best_algo, times
