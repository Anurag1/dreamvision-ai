# DreamVision AI

**DreamVision AI** converts visual descriptions into an explicit scene graph, then uses that structure to create a constraint-aware image prompt. This repository includes an optional multimodal image-generation adapter and a paired benchmark against a conventional single-pass text-to-image prompt.

> Research status: experimental prototype. The benchmark harness is implemented, but no live model-comparison results are claimed until it is run with provider credentials and generated images are evaluated. The original structural-completeness score is not a measure of image quality or human dream vividness.

## Implemented

- Deterministic scene parsing: object hints, simple attributes, spatial relations, missing-detail flags, and warnings.
- Two prompt conditions using the same source description:
  - `direct_baseline`: conventional single-pass prompt, passed through unchanged.
  - `dreamvision_structured`: same description augmented with extracted objects, attributes, relations, and ambiguity warnings.
- Optional OpenAI image generation adapter (`gpt-image-1` by default).
- Optional vision judge (`gpt-4o` by default) that scores object, relation, attribute, and overall fidelity from each generated image.
- Paired benchmark runner writes raw JSON and CSV, including model IDs, prompt hashes, timing, dataset hash, and environment metadata.
- Offline unit tests run without API credentials.

## Offline quick start

```bash
python -m unittest discover -s tests -v
python demo.py
```

These tests validate parsing and prompt construction only. They do not generate images or establish comparative model performance.

## Run the multimodal benchmark

Python 3.10+ is recommended.

```bash
python -m pip install -r requirements.txt
export OPENAI_API_KEY="..."
python run_benchmark.py \
  --dataset benchmarks/scenes.json \
  --output benchmark_runs/run-001 \
  --image-model gpt-image-1 \
  --judge-model gpt-4o \
  --repeats 3 \
  --seed 17
```

The runner creates two images per task and repeat in randomized condition order. It evaluates each image independently against explicit required objects, relations, and attributes. It writes `results.json`, `results.csv`, and generated image artifacts. Then analyze paired differences:

```bash
python analyze_results.py benchmark_runs/run-001/results.json
```

The analysis reports mean and median DreamVision-minus-direct paired differences and a deterministic paired-bootstrap percentile interval. The bootstrap seed is separate from the image-generation ordering seed.

## Experimental design

The comparison isolates **prompt-construction strategy**: both conditions use the same image model, size, dataset, evaluator, and repeat count. The direct baseline sends the description unchanged. DreamVision adds only facts extracted by the current parser; it must not invent unmentioned scene content. The task and condition order are shuffled with a recorded seed. Image generation itself is stochastic; the seed controls ordering, not provider-side sampling.

Primary judge metrics (0–5): object fidelity, spatial-relation fidelity, attribute fidelity, and overall scene fidelity. The vision judge is a model-based evaluator and may have systematic bias. For a publishable claim, use multiple independent judge models, blind condition labels, add human ratings, report uncertainty, and retain all images and raw records. Do not describe judge scores as objective ground truth.

## Dataset and reproducibility

`benchmarks/scenes.json` contains eight pilot scenes with required objects, relations, and attributes. Extend it only with versioned changes and preserve the exact dataset used for every run. The dataset SHA-256 is recorded in the result manifest.

Record exact image and judge model IDs, run date, package versions, dataset hash, prompt hashes, image dimensions, repeat count, ordering seed, per-image scores, and failures. Run at least three repeats and report per-task paired differences. Audit a sample with human annotators. The seed does not make provider image generation deterministic.

## Current evidence status

The repository has an implemented multimodal pipeline, benchmark harness, and offline test suite. No live image-generation experiment has been executed as part of this commit, so there are **no empirical comparative results yet**. This is intentional: publishing fabricated scores would invalidate the experiment. Run the benchmark with an API key to create the first result artifact.

## Limitations

The parser is a lightweight lexical baseline, not a trained scene-graph model. The judge may be biased by its own visual-language capabilities. Image generation is stochastic and provider-dependent. The eight-scene dataset is a pilot, not representative of all visual prompts. This project does not measure dream perception, cognition, or the fidelity of a person's private mental imagery.

## Project layout

```text
benchmarks/scenes.json
dreamvision/{engine,prompting,multimodal,benchmark}.py
tests/
run_benchmark.py
analyze_results.py
EXPERIMENT_PROTOCOL.md
requirements.txt
SKILL.md
```
