from __future__ import annotations

import os

from .api import sort, select_algorithm
from .config import get_artifacts_dir, get_env_bool, get_seed
from .installer import train_thresholds, save_thresholds, load_thresholds
from .optimize import gen_cases, optimize_cutoffs

__all__ = ["sort", "select_algorithm", "features", "algorithms", "baseline", "model"]


def _maybe_init_on_import() -> None:
    if not get_env_bool("MLSORT_INIT_ON_IMPORT", False):
        return
    thr_path = os.path.join(get_artifacts_dir(), "thresholds.json")
    if os.path.exists(thr_path):
        return
    os.makedirs(os.path.dirname(thr_path) or ".", exist_ok=True)
    seed = get_seed()
    th = train_thresholds(num_samples=600, max_n=120_000, seed=seed, max_depth=3)
    save_thresholds(thr_path, th)
    arrays = gen_cases(num_samples=250, max_n=120_000, seed=seed + 7)
    res = optimize_cutoffs(th, arrays)
    th.cutoff_n = int(res["best"]["cutoff_n"])  # type: ignore[attr-defined]
    th.activation_n = int(res["best"]["activation_n"])  # type: ignore[attr-defined]
    save_thresholds(thr_path, th)


_maybe_init_on_import()
