# DreamVision paired image-prompt benchmark protocol

## Research question
Does adding an explicit, parser-derived scene graph to an otherwise identical image-generation request improve adherence to stated objects, spatial relations, and attributes compared with a conventional single-pass prompt?

## Conditions
- **A — Conventional direct-prompt baseline:** send the original natural-language scene description unchanged to the image-generation model.
- **B — DreamVision structured prompt:** augment the same description with objects, attributes, and spatial relations extracted by `analyze_scene`.

Both conditions use the same image model, image size, task, and evaluator. Condition order is randomized within each task/repeat. The benchmark is paired by task and repeat. This isolates prompt-construction strategy; it does not claim DreamVision is a better foundation model.

## Dataset and unit of analysis
The pilot dataset is `benchmarks/scenes.json` (eight tasks). One generated image is one observation; task-repeat pairs are the primary paired unit. The pilot is too small for broad generalization.

## Outcomes
A vision judge assigns integer scores from 0 to 5 for object fidelity, relation fidelity, attribute fidelity, and overall fidelity. It must cite visible evidence and list missing/wrong items. These are model-judged outcomes, not ground truth.

## Analysis plan
Run `python analyze_results.py benchmark_runs/run-001/results.json`. For each metric, calculate per-task/repeat paired differences (DreamVision minus direct), the mean paired difference, median paired difference, and a paired bootstrap 95% percentile interval. Report all task-level values and all failures. If multiple judge models are used, report each judge separately before any pooled summary. Human ratings should be collected blind to condition for confirmatory claims.

## Reproducibility
Every run stores exact model identifiers, dataset SHA-256, prompt SHA-256, environment versions, seed, image dimensions, timestamps, latency, prompts, and raw judge outputs. The seed controls task/condition ordering only; it does not make image generation deterministic.

## Current evidence status
The repository includes code and offline unit tests for parsing and prompt construction. No live image-generation experiment has been executed as part of this commit, so there are no empirical comparative results yet. Never replace this statement with an invented win rate or performance claim.
