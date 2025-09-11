from __future__ import annotations

import argparse
import os

from mlsort.installer import train_thresholds, save_thresholds


def main():
    parser = argparse.ArgumentParser(description="Benchmark and derive thresholds for mlsort")
    parser.add_argument("--samples", type=int, default=1200)
    parser.add_argument("--max-n", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument("--out", type=str, default=os.path.join(os.path.expanduser("~"), ".cache", "mlsort", "thresholds.json"))
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    th = train_thresholds(num_samples=args.samples, max_n=args.max_n, seed=args.seed, max_depth=args.max_depth)
    save_thresholds(args.out, th)
    print(f"Saved thresholds to {args.out}")  # noqa: T201


if __name__ == "__main__":
    main()
