#!/usr/bin/env python3
import argparse
import json
import os
from dreamvision.benchmark import run_benchmark

def main():
    parser = argparse.ArgumentParser(description="Run paired DreamVision vs direct-prompt image benchmark")
    parser.add_argument("--dataset", default="benchmarks/scenes.json")
    parser.add_argument("--output", default="benchmark_runs/latest")
    parser.add_argument("--image-model", default=os.getenv("DREAMVISION_IMAGE_MODEL", "gpt-image-2.5-flare"))
    parser.add_argument("--judge-model", default=os.getenv("DREAMVISION_JUDGE_MODEL", "gpt-4o"))
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--size", default="1024x1024")
    parser.add_argument("--seed", type=int, default=17)
    args = parser.parse_args()
    if not os.getenv("OPENAI_API_KEY"):
        parser.error("OPENAI_API_KEY is required for live image generation and vision evaluation")
    report = run_benchmark(args.dataset, args.output, args.image_model, args.judge_model,
                           args.repeats, args.size, args.seed)
    print(json.dumps(report["summary"], indent=2))
    print(f"Saved: {args.output}/results.json and results.csv")

if __name__ == "__main__":
    main()
