from __future__ import annotations

import statistics
import time
from typing import Dict, List, Tuple

import numpy as np

from .decision import decide
from .installer import Thresholds
from .algorithms import time_algorithm
from .data import (
    gen_sorted, gen_reverse, gen_nearly_sorted, gen_uniform, gen_small_range, gen_zipf, gen_normal,
)


def gen_cases(num_samples: int, max_n: int, seed: int) -> List[np.ndarray]:
    rng = np.random.default_rng(seed)
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
    cases = []
    for _ in range(num_samples):
        n = int(rng.integers(128, max_n + 1))
        g = gens[int(rng.integers(0, len(gens)))]
        cases.append(g(n))
    return cases


def essential_stats(vals: List[float]) -> Dict[str, float]:
    vals_sorted = sorted(vals)
    return {
        "mean": float(statistics.fmean(vals)),
        "median": float(vals_sorted[len(vals_sorted)//2]),
    }


def eval_policy(th: Thresholds, arrays: List[np.ndarray]) -> Dict[str, float]:
    total_times: List[float] = []
    for arr in arrays:
        t0 = time.perf_counter()
        algo = decide(arr, th)
        t1 = time.perf_counter()
        t_sort = time_algorithm(arr, algo, repeats=1)
        total_times.append((t1 - t0) + t_sort)
    return essential_stats(total_times)


def grid_candidates(max_n: int) -> Tuple[List[int], List[int]]:
    cutoff_grid = [32, 64, 96, 128, 192, 256, 384, 512, 768, 1024, 1536, 2048, 3072, 4096]
    cutoff_grid = [c for c in cutoff_grid if c < max_n]
    act_grid_base = [8192, 12000, 16384, 24576, 32768, 49152, 65536, 98304, 131072]
    act_grid = sorted({min(max_n, a) for a in act_grid_base if a <= max_n})
    if not act_grid:
        act_grid = [min(max_n, 8192)]
    return cutoff_grid, act_grid


def optimize_cutoffs(th: Thresholds, arrays: List[np.ndarray]) -> Dict:
    cutoff_grid, act_grid = grid_candidates(max(len(a) for a in arrays))
    best = {"mean": float("inf"), "cutoff_n": th.cutoff_n, "activation_n": getattr(th, "activation_n", th.cutoff_n * 4)}
    tried = []
    for c in cutoff_grid:
        for a in act_grid:
            if a <= c:
                continue
            th_try = Thresholds(cutoff_n=c, activation_n=a, tree=th.tree, feature_names=th.feature_names)
            stats = eval_policy(th_try, arrays)
            tried.append({"cutoff_n": c, "activation_n": a, **stats})
            if stats["mean"] < best["mean"]:
                best = {"mean": stats["mean"], "cutoff_n": c, "activation_n": a}
    top = sorted(tried, key=lambda x: x["mean"])[:10]
    return {"best": best, "tried": top}
