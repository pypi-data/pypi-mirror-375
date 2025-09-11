from __future__ import annotations

from typing import Dict

from .algorithms import ALG_COUNTING, ALG_NP_MERGE, ALG_NP_QUICK, ALG_RADIX, ALG_TIMSORT


def heuristic_baseline(props: Dict[str, float]) -> str:
    n = props["n"]
    dtype = int(props["dtype_code"])  # 0 float, 1 int
    sortedness = props["est_sortedness"]
    dup_ratio = props["est_dup_ratio"]
    rng = props["est_range"]
    entropy = props["est_entropy"]
    run_len = props["est_run_len"]

    # If almost sorted or long runs, Timsort shines
    if sortedness >= 0.9 or run_len >= 32:
        return ALG_TIMSORT

    if dtype == 1:
        # Counting sort when range relatively small and many duplicates
        if rng > 0 and rng <= max(1024.0, 8.0 * n) and dup_ratio >= 0.3 and entropy <= 0.7:
            return ALG_COUNTING
        # Radix for wide range ints with moderate entropy
        if n >= 512 and entropy <= 0.9:
            return ALG_RADIX

    # For general cases prefer NumPy quicksort for speed, merge for stability/some patterns
    if n >= 2000:
        return ALG_NP_QUICK
    else:
        return ALG_NP_MERGE
