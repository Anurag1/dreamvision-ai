# DreamVision AI

DreamVision AI is an experimental cognitive-visualization skill. It turns a natural-language scene description into a structured scene graph, flags missing information, checks simple spatial constraints, and produces a transparent quality report.

It does **not** claim to reproduce dreams or measure human visual perception. Its scores evaluate the structure of the supplied description only.

## Quick start

```bash
python demo.py
python -m unittest discover -s tests -v
```

No external dependencies or API keys required.

## Pipeline

1. Extract entities and attributes from text.
2. Detect spatial and relational phrases.
3. Build a lightweight scene graph.
4. Identify unspecified scene dimensions.
5. Check simple contradictions and report evidence.
6. Score completeness and constraint coverage.

## Python API

```python
from dreamvision import analyze_scene

result = analyze_scene(
    "A red bicycle stands beside a wooden bench under a tree."
)
print(result.to_dict())
```

## Limitations

This is a deterministic baseline, not a vision model or a substitute for a multimodal LLM. It does not infer hidden scene details as facts. Its phrase extraction is intentionally simple and should be benchmarked against human annotations before being used for research claims.
