import json
from dreamvision import analyze_scene

scene = (
    "A small red bicycle stands beside a wooden bench under a tree "
    "in a quiet garden at sunset, viewed at eye level."
)
result = analyze_scene(scene)
print("DREAMVISION AI — LIVE DEMO")
print("=" * 48)
print(json.dumps(result.to_dict(), indent=2))
print("\nNEXT CLARIFICATION:")
print("What material is the bicycle frame, and how far is it from the bench?")
