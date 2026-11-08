---
name: dreamvision
description: Convert visual ideas into explicit scene structures, construct constraint-aware image prompts, and evaluate generated scenes against stated requirements.
---

# DreamVision AI Skill

## Objective
Help a user externalize a mental image as a structured, inspectable scene description and optionally generate/evaluate a visual rendering.

## Procedure
1. Accept a free-form scene description.
2. Extract objects, attributes, and explicit spatial relations.
3. Preserve uncertainty; never convert an unspecified detail into a claimed fact.
4. Identify missing dimensions and possible contradictions.
5. Offer two image-prompt conditions for experiments: direct description baseline and structured DreamVision prompt.
6. If image generation is configured, generate images with the same provider/model and settings for both conditions.
7. Evaluate generated images against a task specification, distinguishing visible evidence from assumptions.
8. Return the scene graph, prompts, images, missing details, evaluation scores, and limitations.

## Benchmark protocol
- Use paired tasks: same description, image model, image size, evaluator, and repeat count.
- Randomize task and condition order; record the seed.
- Preserve prompts, prompt hashes, image artifacts, model IDs, dataset hash, environment, latency, scores, and failures.
- Compare per-task paired differences; report mean/median and uncertainty.
- Treat model-judge ratings as model-based assessments, not ground truth. Use independent judges and blind human ratings before making efficacy claims.
- Do not claim deterministic image generation; ordering seeds do not control provider-side sampling.

## Epistemic and safety rules
- Distinguish input facts, parser-derived facts, generated content, and judge interpretations.
- Do not claim to know what a person dreamed beyond their description.
- Do not claim this system measures intelligence, creativity, mental health, neurological function, or human dream vividness.
- Do not claim dream imagery is objectively more accurate than waking imagery.
- Do not invent benchmark results or suppress failed generations.
- Do not publish secrets, API keys, or private user images without authorization.

## Output contract
Use JSON-compatible fields: `objects`, `relations`, `unknowns`, `warnings`, `scores`, `summary`, and (when multimodal execution is enabled) `images`, `prompts`, `model_metadata`, and `evaluation`.
