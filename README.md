# DreamVision AI

**DreamVision AI** converts visual descriptions into an explicit scene graph, then uses that structure to create a constraint-aware image prompt. This repository includes an optional multimodal image-generation adapter and a paired benchmark against a conventional single-pass text-to-image prompt.

> Research status: experimental prototype. The benchmark harness is implemented, but no live model-comparison results are claimed until it is run with provider credentials and generated images are evaluated. The original structural-completeness score is not a measure of image quality or human dream vividness.

## Implemented

- Deterministic scene parsing: object hints, simple attributes, spatial relations, missing-detail flags, and warnings.
- Two prompt conditions using the same source description:
  - `direct_baseline`: conventional single-pass prompt, passed through unchanged.
  - `dreamvision_structured`: same description augmented with extracted objects, attributes, relations, and ambiguity warnings.
- Optional OpenAI image generation adapter (`gpt-image-2.5-flare` by default).
- Optional vision judge (`gpt-4o` by default) that scores object, relation, attribute, and overall fidelity from each generated image.
- Paired benchmark runner writes raw JSON and CSV, including model IDs, prompt hashes, timing, dataset hash, and environment metadata.
- Offline unit tests run without API credentials.

## Offline quick start

```bash
python -m unittest discover -s tests -v
python demo.py
```

These tests validate parsing and prompt construction only. They do not generate images or establish comparative model performance. See [TEST_RESULTS.md](TEST_RESULTS.md) for the recorded offline test run.

## Run the multimodal benchmark

Python 3.10+ is recommended.

```bash
python -m pip install -r requirements.txt
export OPENAI_API_KEY="..."
python run_benchmark.py \
  --dataset benchmarks/scenes.json \
  --output benchmark_runs/run-001 \
  --image-model gpt-image-2.5-flare \
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


## Cross-model and independent evaluation

The expanded runner compares at least two image-generation model IDs and evaluates each image with at least two separate vision-judge model IDs. It creates a blinded human-rating CSV and keeps the image/condition key in a separate restricted file.

Use model IDs enabled for your API account. Current documented examples include `gpt-image-2`, `gpt-image-2.5-sunburst`, and `gpt-image-2.5-flare`. See the [official image generation guide](https://developers.openai.com/api/docs/guides/image-generation).

```bash
python run_multimodel_benchmark.py \
  --image-models gpt-image-2,gpt-image-2.5-sunburst \
  --judge-models gpt-4o,gpt-4.1 \
  --repeats 3 \
  --seed 17 \
  --output benchmark_runs/multimodel-001
```

Analyze each image-model × judge-model pairing separately:

```bash
python analyze_multimodel_results.py benchmark_runs/multimodel-001/results.json
```

For blind human assessment, share only `human_ratings_blinded.csv` and the corresponding files in `blinded_images/`. Keep `blind_key_restricted.json` private until ratings are complete. Never share the key with raters.

The API account must have access to every requested model. Image generation and vision evaluation can incur API charges; obtain the account owner's permission and set usage limits before running a large benchmark. The pilot default of 8 scenes × 3 repeats × 2 image models × 2 conditions produces 96 images, each evaluated by both judges.


## Discovery-first experiment: which structures benefit?

The research objective is not to maximize one aggregate benchmark score. It is to identify *where* explicit structure helps, does nothing, or hurts.

The multimodel runner now has four prompt arms:
- `direct_baseline`: original description unchanged.
- `objects_only`: extracted entities and explicit object attributes.
- `relations_only`: extracted spatial relationships.
- `graph_full`: entities, attributes, relations, and ambiguity warnings.

The pilot scene manifest is annotated with object count, relation count/type, constraint density, compositional depth, ambiguity, and attribute types. These labels are hypotheses for stratification, not validated ground truth.

Run the factor analysis after the main run:

```bash
python analyze_scene_factors.py benchmark_runs/multimodel-001/results.json
```

### Questions the experiment is designed to answer

1. Do left/right, above/below, containment, support, and occlusion-like relationships benefit equally?
2. Does relations-only prompting help more than objects-only prompting when spatial constraints are dense?
3. Does graph prompting help more as object count and relation count increase?
4. Are multi-hop compositions harder than pairwise relations?
5. Does explicit structure help resolve ambiguity, or does a parser turn ambiguity into incorrect certainty?
6. Which attributes (color, material, count, state, lighting, depth) are preserved better?
7. Are effects consistent across image models, or model-specific?

### Interpretation guardrails

- Do not infer a factor effect from one or two scenes. Add independently authored scenes per factor level and repeat across seeds.
- Report all four prompt arms separately. A full-graph gain with no relations-only gain may come from entity/attribute enumeration rather than graph structure.
- A relations-only gain is more direct evidence that relation encoding helps, but still requires human verification and scene-level replication.
- Keep prompt length/token budget comparable or add a length-matched control. Otherwise extra words are a confound.
- Vision-model scores are noisy proxies. Blind human raters should judge images without seeing condition, model, or hypothesis.
- Report negative effects, parser extraction errors, evaluator disagreement, and per-scene failures.
- Do not claim causal discovery from descriptive subgroup means. Pre-register hypotheses and use a sufficiently powered, balanced scene set before confirmatory claims.

The current eight-scene manifest is a pilot for checking the pipeline and generating hypotheses. It is not sufficiently large or balanced to establish which visual factors benefit.
