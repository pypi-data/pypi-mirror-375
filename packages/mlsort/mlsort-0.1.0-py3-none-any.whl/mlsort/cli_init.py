from __future__ import annotations

import argparse
import os

from mlsort.config import get_artifacts_dir, get_seed
from mlsort.installer import train_thresholds, save_thresholds, load_thresholds
from mlsort.optimize import gen_cases, optimize_cutoffs


def main():
    parser = argparse.ArgumentParser(description="Initialize mlsort artifacts; optional params have defaults")
    parser.add_argument("--samples", type=int, default=1200, help="training samples")
    parser.add_argument("--max-n", type=int, default=200000, help="max array size in benchmarking")
    parser.add_argument("--seed", type=int, default=None, help="random seed; default from MLSORT_SEED or 42")
    parser.add_argument("--artifacts", type=str, default=None, help="artifacts dir; default MLSORT_ARTIFACTS_DIR or OS cache")
    args = parser.parse_args()

    seed = args.seed if args.seed is not None else get_seed()
    artifacts = args.artifacts or get_artifacts_dir()
    thr_path = os.path.join(artifacts, "thresholds.json")
    os.makedirs(artifacts, exist_ok=True)

    th = train_thresholds(num_samples=args.samples, max_n=args.max_n, seed=seed, max_depth=3)
    save_thresholds(thr_path, th)

    arrays = gen_cases(num_samples=min(300, args.samples), max_n=args.max_n, seed=seed + 17)
    res = optimize_cutoffs(load_thresholds(thr_path), arrays)
    th_best = load_thresholds(thr_path)
    th_best.cutoff_n = int(res["best"]["cutoff_n"])  # type: ignore[attr-defined]
    th_best.activation_n = int(res["best"]["activation_n"])  # type: ignore[attr-defined]
    save_thresholds(thr_path, th_best)

    print({"artifacts": artifacts, "thresholds": thr_path, "best": res["best"]})  # noqa: T201


if __name__ == "__main__":
    main()
