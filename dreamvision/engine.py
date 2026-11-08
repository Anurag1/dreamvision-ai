from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import re

OBJECT_HINTS = {
    "person", "woman", "man", "child", "dog", "cat", "bird", "tree",
    "house", "building", "mountain", "river", "lake", "sun", "moon",
    "cloud", "car", "bicycle", "bench", "table", "chair", "door",
    "window", "bridge", "road", "boat", "book", "phone", "robot",
    "machine", "flower", "mountain", "castle", "train", "street"
}
COLORS = {"red", "blue", "green", "yellow", "black", "white", "golden",
          "orange", "purple", "pink", "brown", "grey", "gray"}
MATERIALS = {"wooden", "metal", "metallic", "glass", "stone", "brick",
             "plastic", "paper", "fabric"}
RELATIONS = {
    "to the left of": "left_of",
    "to the right of": "right_of",
    "in front of": "in_front_of",
    "behind": "behind",
    "beside": "beside",
    "next to": "beside",
    "under": "under",
    "beneath": "under",
    "above": "above",
    "over": "above",
    "inside": "inside",
    "within": "inside",
    "near": "near",
    "on": "on"
}

@dataclass
class SceneAnalysis:
    summary: str
    objects: List[Dict[str, Any]]
    relations: List[Dict[str, str]]
    unknowns: List[str]
    warnings: List[str]
    scores: Dict[str, float]

    def to_dict(self):
        return asdict(self)


def _tokens(text):
    return re.findall(r"[a-zA-Z]+(?:'[a-z]+)?", text.lower())


def _extract_objects(tokens):
    found = []
    for i, token in enumerate(tokens):
        if token in OBJECT_HINTS:
            attrs = []
            if i > 0 and tokens[i-1] in COLORS:
                attrs.append({"type": "color", "value": tokens[i-1]})
            if i > 0 and tokens[i-1] in MATERIALS:
                attrs.append({"type": "material", "value": tokens[i-1]})
            found.append({"name": token, "attributes": attrs})
    counts, result = {}, []
    for item in found:
        counts[item["name"]] = counts.get(item["name"], 0) + 1
        result.append({"id": f'{item["name"]}_{counts[item["name"]]}', **item})
    return result


def _extract_relations(text, objects):
    lower = text.lower()
    names = sorted({o["name"] for o in objects}, key=len, reverse=True)
    out = []
    for phrase, relation in sorted(RELATIONS.items(), key=lambda x: -len(x[0])):
        for subject in names:
            for obj in names:
                if subject == obj:
                    continue
                pattern = (
                    rf"\b{re.escape(subject)}\b"
                    rf"(?:\s+\w+){{0,3}}?\s+{re.escape(phrase)}\s+"
                    rf"(?:a\s+|an\s+|the\s+)?(?:\w+\s+){{0,2}}?{re.escape(obj)}\b"
                )
                if re.search(pattern, lower):
                    item = {"subject": subject, "relation": relation, "object": obj}
                    if item not in out:
                        out.append(item)
    return out


def analyze_scene(description: str) -> SceneAnalysis:
    if not isinstance(description, str) or not description.strip():
        raise ValueError("description must be a non-empty string")

    tokens = _tokens(description)
    objects = _extract_objects(tokens)
    relations = _extract_relations(description, objects)
    lower = description.lower()

    unknowns = []
    if not any(x in lower for x in ("from above", "eye level", "low angle", "close-up", "wide shot", "first person")):
        unknowns.append("camera angle / viewpoint")
    if not any(x in lower for x in ("sunlight", "moonlight", "bright", "dark", "lit", "lighting", "sunset", "sunrise")):
        unknowns.append("lighting / time of day")
    if not any(x in lower for x in ("large", "small", "tiny", "huge", "giant", "life-sized")):
        unknowns.append("relative size or scale")
    if not any(x in lower for x in ("forest", "city", "street", "room", "beach", "mountain", "field", "garden", "background")):
        unknowns.append("background and environment")
    if not any(o["attributes"] and any(a["type"] == "material" for a in o["attributes"]) for o in objects):
        unknowns.append("surface materials")

    warnings = []
    relation_pairs = {(r["subject"], r["relation"], r["object"]) for r in relations}
    for a, b in (("left_of", "right_of"), ("above", "under"), ("in_front_of", "behind")):
        for subject, relation, obj in list(relation_pairs):
            if relation == a and (obj, b, subject) in relation_pairs:
                warnings.append(f"Potentially conflicting relations: {subject} {a} {obj}, but {obj} {b} {subject}.")
    if not objects:
        warnings.append("No recognizable objects found; provide concrete nouns for a stronger scene graph.")
    if not relations and len(objects) > 1:
        warnings.append("Multiple objects found, but no explicit spatial relationship was detected.")

    object_score = min(1.0, len(objects) / 4.0)
    relation_score = 1.0 if len(objects) <= 1 else min(1.0, len(relations) / (len(objects) - 1))
    detail_score = max(0.0, 1.0 - len(unknowns) / 5.0)
    consistency_score = 0.0 if any("conflicting" in warning for warning in warnings) else 1.0
    overall = round(100 * (0.30*object_score + 0.30*relation_score +
                           0.25*detail_score + 0.15*consistency_score), 1)

    return SceneAnalysis(
        summary=description.strip(),
        objects=objects,
        relations=relations,
        unknowns=unknowns,
        warnings=warnings,
        scores={
            "object_coverage": round(object_score, 2),
            "relation_coverage": round(relation_score, 2),
            "detail_specification": round(detail_score, 2),
            "consistency": round(consistency_score, 2),
            "structural_completeness_0_to_100": overall
        }
    )
