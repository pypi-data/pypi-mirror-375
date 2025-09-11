from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

from .algorithms import measure_best_algorithm
from .features import estimate_properties


@dataclass
class Sample:
    X: List[float]
    y: str
    props: Dict[str, float]


# Generators

def gen_sorted(n: int, dtype: str = "int") -> Sequence:
    if dtype == "int":
        return np.arange(n, dtype=np.int32)
    else:
        return np.linspace(0.0, 1.0, n, dtype=np.float64)


def gen_reverse(n: int, dtype: str = "int") -> Sequence:
    if dtype == "int":
        return np.arange(n, 0, -1, dtype=np.int32)
    else:
        return np.linspace(1.0, 0.0, n, dtype=np.float64)


def gen_nearly_sorted(n: int, swaps: int = 10, dtype: str = "int") -> Sequence:
    a = gen_sorted(n, dtype)
    a = np.array(a, copy=True)
    swaps = min(swaps, max(1, n // 50))
    for _ in range(swaps):
        i = random.randrange(n)
        j = random.randrange(n)
        a[i], a[j] = a[j], a[i]
    return a


def gen_uniform(n: int, dtype: str = "int", low: int = 0, high: int = 10000) -> Sequence:
    if dtype == "int":
        return np.random.randint(low, high, size=n, dtype=np.int32)
    else:
        return np.random.uniform(0.0, 1.0, size=n).astype(np.float64)


def gen_small_range(n: int, k: int = 256) -> Sequence:
    # ints with many duplicates
    return np.random.randint(0, k, size=n, dtype=np.int32)


def gen_zipf(n: int, a: float = 2.0, dtype: str = "int", max_val: int = 100000) -> Sequence:
    # Zipf distributed positive integers, clipped
    vals = np.random.zipf(a, size=n)
    vals = np.clip(vals, 0, max_val)
    if dtype == "int":
        return vals.astype(np.int32)
    else:
        return vals.astype(np.float64)


def gen_normal(n: int, mean: float = 0.0, std: float = 1.0, dtype: str = "float") -> Sequence:
    vals = np.random.normal(mean, std, size=n)
    if dtype == "int":
        return vals.round().astype(np.int32)
    else:
        return vals.astype(np.float64)


def synthesize_dataset(num_samples: int, max_n: int, seed: int = 42):
    random.seed(seed)
    import numpy as _np
    _np.random.seed(seed)
    samples = []
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
    for _ in range(num_samples):
        n = random.randint(128, max_n)
        g = random.choice(gens)
        arr = g(n)
        props = estimate_properties(arr)
        # Measure which algorithm is best for this concrete arr
        label, _times = measure_best_algorithm(arr, repeats=1)
        X = [
            props["n"],
            props["dtype_code"],
            props["est_sortedness"],
            props["est_dup_ratio"],
            props["est_range"],
            props["est_entropy"],
            props["est_run_len"],
        ]
        samples.append(Sample(X=X, y=label, props=props))
    return samples
