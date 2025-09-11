from __future__ import annotations

import argparse
import os

from mlsort.config import get_artifacts_dir, get_seed
from mlsort.installer import load_thresholds, save_thresholds
from mlsort.optimize import gen_cases, optimize_cutoffs


def main():
    parser = argparse.ArgumentParser(description="Optimize cutoff and activation thresholds")
    parser.add_argument("--samples", type=int, default=350)
    parser.add_argument("--max-n", type=int, default=100000)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--thresholds", type=str, default=None)
    args = parser.parse_args()

    seed = args.seed if args.seed is not None else get_seed()
    thr_path = args.thresholds or os.path.join(get_artifacts_dir(), "thresholds.json")
    th = load_thresholds(thr_path)

    arrays = gen_cases(args.samples, args.max_n, seed=seed + 10)
    res = optimize_cutoffs(th, arrays)

    th.cutoff_n = int(res["best"]["cutoff_n"])  # type: ignore[attr-defined]
    th.activation_n = int(res["best"]["activation_n"])  # type: ignore[attr-defined]
    save_thresholds(thr_path, th)

    print({"best": res["best"], "thresholds": thr_path})  # noqa: T201


if __name__ == "__main__":
    main()
