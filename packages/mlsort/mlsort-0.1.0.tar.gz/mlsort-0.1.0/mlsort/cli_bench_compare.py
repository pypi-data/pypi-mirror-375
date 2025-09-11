from __future__ import annotations

import argparse
import json
import os

from mlsort.benchmark import run_benchmark


def main():
    parser = argparse.ArgumentParser(description="Benchmark decision policy vs naive baselines")
    parser.add_argument("--samples", type=int, default=600)
    parser.add_argument("--max-n", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--thresholds", type=str, default=os.path.join(os.path.expanduser("~"), ".cache", "mlsort", "thresholds.json"))
    parser.add_argument("--out-json", type=str, default="bench_compare.json")
    parser.add_argument("--out-md", type=str, default="report.md")
    args = parser.parse_args()

    results = run_benchmark(args.samples, args.max_n, args.seed, args.thresholds)

    with open(args.out_json, "w") as f:
        json.dump(results, f, indent=2)

    md = []
    md.append("# mlsort: Decision Policy vs. Naive Single-Choice\n\n")
    md.append(f"- Samples: {results['samples']}  \n- Max n: {results['max_n']}  \n- Seed: {results['seed']}  \n- Thresholds: {results['thresholds']}\n\n")
    md.append("## Mean/Median/P90 (seconds)\n")
    md.append(f"- Decision mean: {results['aggregate']['decision']['mean']:.6f}\n")
    for k, v in results['aggregate'].items():
        if k == 'decision':
            continue
        md.append(f"- {k} mean: {v['mean']:.6f}\n")
    md.append(f"\nBest naive: {results['best_naive']['key']} at {results['best_naive']['mean_time']:.6f} s\n")
    md.append(f"Speedup vs best naive: {results['speedup_vs_best_naive']:.3f}x\n")

    with open(args.out_md, "w") as f:
        f.write("".join(md))

    print(f"Wrote {args.out_json} and {args.out_md}")  # noqa: T201


if __name__ == "__main__":
    main()
