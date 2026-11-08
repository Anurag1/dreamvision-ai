# Cross-model independent evaluation protocol

## Research question
Does an explicit graph-derived prompt improve image adherence to a scene specification relative to passing the original description directly, and does any effect replicate across image-generation models?

## Design
- Minimum 2 image-generation models, 2 independent vision-judge models, 8 pilot scenes, 3 repeats.
- For each image model, each task/repeat is paired: direct baseline vs DreamVision structured prompt.
- Randomize condition order; record the ordering seed. Do not imply the seed controls model sampling.
- Each judge evaluates every image independently. Report each judge separately; do not silently average disagreements.
- Export opaque image IDs for blind human ratings. Raters must not receive the condition key or model metadata.
- Use identical image dimensions and benchmark requirements for both conditions within a model.

## Primary outcomes
Object, relation, attribute, and overall fidelity, each rated 0-5. Report paired effects separately for every image-model × judge-model combination. The bootstrap interval resamples task-repeat pairs and is descriptive for this pilot.

## Human validation
Collect at least two independent blind human ratings per image where feasible. Use the provided human_ratings_blinded.csv. Keep blind_key_restricted.json separate from raters. Report inter-rater agreement and human paired effects. Do not call model-based judging "independent human evaluation".

## Interpretation
Evidence for improvement requires positive paired effects that replicate across multiple image models and judges, with human ratings directionally consistent. If judge models disagree or human results do not replicate, report that. This small pilot is exploratory and not sufficient for broad claims.

## Reporting
Publish the raw JSON, CSV, image artifacts (subject to provider terms and privacy), exact model identifiers, dataset hash, prompts, errors, latency, and analysis output. Report all failed generations. Never fabricate or selectively omit results.

## Current execution status
The benchmark code and offline tests can be executed locally. A live cross-model run requires valid API credentials and access to at least two image models and two vision-capable judges. No live cross-model scores should be claimed until that run and blind human evaluation are completed.
