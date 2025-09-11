from __future__ import annotations

import json
import os
import statistics
import time
from typing import Dict, List

import numpy as np

from .algorithms import (
    ALG_NP_MERGE,
    ALG_NP_QUICK,
    ALG_TIMSORT,
    time_algorithm,
)
from .decision import decide
from .installer import load_thresholds, train_thresholds, save_thresholds
from .data import (
    gen_sorted, gen_reverse, gen_nearly_sorted, gen_uniform, gen_small_range, gen_zipf, gen_normal,
)


Naive = [ALG_TIMSORT, ALG_NP_QUICK, ALG_NP_MERGE]


def ensure_thresholds(path: str, samples: int, max_n: int, seed: int) -> str:
    if os.path.exists(path):
        return path
    th = train_thresholds(num_samples=samples, max_n=max_n, seed=seed, max_depth=3)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    save_thresholds(path, th)
    return path


def _random_case(rng: np.random.Generator, max_n: int):
    n = int(rng.integers(128, max_n + 1))
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
    g = gens[int(rng.integers(0, len(gens)))]
    arr = g(n)
    return arr


def run_benchmark(num_samples: int, max_n: int, seed: int, thresholds_path: str) -> Dict:
    ensure_thresholds(thresholds_path, samples=max(600, num_samples // 2), max_n=max_n, seed=seed)
    th = load_thresholds(thresholds_path)

    rng = np.random.default_rng(seed + 101)

    times_decision: List[float] = []
    times_naive: Dict[str, List[float]] = {k: [] for k in Naive}
    per_case: List[Dict] = []

    for _ in range(num_samples):
        arr = _random_case(rng, max_n)

        t0 = time.perf_counter()
        algo = decide(arr, th)
        t1 = time.perf_counter()
        t_sort = time_algorithm(arr, algo, repeats=1)
        t_decision_total = (t1 - t0) + t_sort
        times_decision.append(t_decision_total)

        for k in Naive:
            t = time_algorithm(arr, k, repeats=1)
            times_naive[k].append(t)

        per_case.append({
            "n": int(len(arr)),
            "decision_algo": algo,
            "decision_total_time": t_decision_total,
            **{f"time_{k}": times_naive[k][-1] for k in Naive},
        })

    def stats(vals: List[float]):
        vals_sorted = sorted(vals)
        p50 = vals_sorted[len(vals_sorted)//2]
        p90 = vals_sorted[int(len(vals_sorted)*0.9)-1]
        return {
            "mean": float(statistics.fmean(vals)),
            "median": float(p50),
            "p90": float(p90),
        }

    agg = {"decision": stats(times_decision)}
    for k in Naive:
        agg[k] = stats(times_naive[k])

    mean_naive = {k: agg[k]["mean"] for k in Naive}
    best_naive_key = min(mean_naive.items(), key=lambda kv: kv[1])[0]
    best_naive_mean = mean_naive[best_naive_key]
    speedup_vs_best = best_naive_mean / agg["decision"]["mean"] if agg["decision"]["mean"] > 0 else 1.0

    win_rates = {}
    for k in Naive:
        wins = sum(1 for i in range(num_samples) if times_decision[i] <= times_naive[k][i])
        win_rates[k] = wins / num_samples

    return {
        "samples": num_samples,
        "max_n": max_n,
        "seed": seed,
        "thresholds": thresholds_path,
        "aggregate": agg,
        "best_naive": {"key": best_naive_key, "mean_time": best_naive_mean},
        "speedup_vs_best_naive": speedup_vs_best,
        "win_rates": win_rates,
        "cases_head": per_case[:50],
    }
