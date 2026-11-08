"""Prompt construction for single-pass and structured DreamVision conditions."""
from .engine import SceneAnalysis

def direct_prompt(description: str) -> str:
    """Conventional single-pass baseline: pass the user description unchanged."""
    return description.strip()

def structured_prompt(description: str, analysis: SceneAnalysis) -> str:
    """Augment the same description with explicit extracted scene graph facts."""
    lines = [
        "Create one coherent image that faithfully depicts the scene below.",
        "Treat the original description as authoritative. Do not add text, labels, or watermarks.",
        f"Original scene description: {description.strip()}",
    ]
    if analysis.objects:
        lines.append("Explicit objects and observed attributes:")
        for obj in analysis.objects:
            attrs = ", ".join(f"{a['type']}={a['value']}" for a in obj["attributes"])
            lines.append(f"- {obj['name']}" + (f" ({attrs})" if attrs else ""))
    if analysis.relations:
        lines.append("Preserve these explicit spatial relationships:")
        for rel in analysis.relations:
            lines.append(f"- {rel['subject']} {rel['relation']} {rel['object']}")
    if analysis.warnings:
        lines.append("Potential ambiguity to avoid:")
        lines.extend(f"- {warning}" for warning in analysis.warnings)
    lines.append("Do not invent specific details that contradict the description.")
    return "\n".join(lines)
