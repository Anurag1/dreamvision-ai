#!/usr/bin/env python3
"""Analyze paired benchmark JSON with a deterministic paired bootstrap."""
import argparse
import json
import random
import statistics
from pathlib import Path
METRICS = ("object_fidelity", "relation_fidelity", "attribute_fidelity", "overall_fidelity")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("results", help="Path to run_benchmark.py results.json")
    parser.add_argument("--bootstrap", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    report = json.loads(Path(args.results).read_text(encoding="utf-8"))
    rows = report["records"]
    index = {(r["task_id"], r["repeat"], r["condition"]): r for r in rows}
    pairs = []
    for task_id, repeat in sorted({(r["task_id"], r["repeat"]) for r in rows}):
        a = index.get((task_id, repeat, "direct_baseline"))
        b = index.get((task_id, repeat, "dreamvision_structured"))
        if a and b:
            pairs.append((a, b))
    if not pairs:
        raise SystemExit("No complete paired task/repeat observations found")
    rng = random.Random(args.seed)
    output = {"paired_observations": len(pairs), "bootstrap_replicates": args.bootstrap,
              "bootstrap_seed": args.seed, "differences": {}}
    for metric in METRICS:
        diffs = [b["scores"][metric] - a["scores"][metric] for a, b in pairs]
        boot = [statistics.mean(diffs[rng.randrange(len(diffs))] for _ in diffs)
                for _ in range(args.bootstrap)]
        boot.sort()
        output["differences"][metric] = {
            "mean_dreamvision_minus_direct": round(statistics.mean(diffs), 3),
            "median_paired_difference": round(statistics.median(diffs), 3),
            "bootstrap_95_percentile_interval": [round(boot[int(.025*len(boot))], 3),
                round(boot[min(len(boot)-1, int(.975*len(boot)))], 3)],
            "task_level_differences": [round(x, 3) for x in diffs]}
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
