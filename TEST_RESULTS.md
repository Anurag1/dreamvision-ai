# Offline test and smoke-test report

**Status:** PASS  
**Executed:** 2026-11-08  
**Scope:** local deterministic tests and dataset/prompt-construction smoke test

## Unit tests

Command:

```bash
python -m unittest discover -s tests -v
```

Result:

```text
Ran 8 tests
OK
```

Coverage includes object/attribute extraction, spatial relation detection, missing-detail detection, empty-input validation, score bounds, direct-baseline input preservation, structured prompt fact inclusion, and uncertainty-preserving prompt wording.

## Dataset smoke test

The eight-scene pilot dataset loaded successfully. For every scene, the direct baseline prompt and DreamVision structured prompt were constructed successfully.

**Result:** 8/8 scene descriptions processed by both prompt builders.

## What this does not establish

No provider-backed image-generation calls or vision-judge calls were executed in this run. Therefore this report does not contain image-fidelity scores and does not establish that DreamVision outperforms a conventional prompt baseline. Run the live benchmark as described in the README to create those empirical results.
