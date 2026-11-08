---
name: dreamvision
description: Convert vague visual ideas into explicit scene structures, identify missing visual details, and check relationships and contradictions.
---

# DreamVision AI Skill

## Objective
Help a user externalize a mental image as a structured, inspectable scene description.

## Procedure
1. Ask for or accept a free-form description of the imagined scene.
2. Extract named objects and descriptive attributes.
3. Extract explicit spatial relations (for example: left of, behind, beside, inside, above).
4. Preserve uncertainty. Never convert an unspecified attribute into a claimed fact.
5. List missing dimensions such as lighting, viewpoint, scale, background, material, and relative position.
6. Check for directly conflicting directional relations when both are explicitly stated.
7. Return:
   - scene summary
   - objects and attributes
   - relations
   - unknowns / questions
   - consistency warnings
   - transparent quality scores

## Safety and epistemic rules
- Distinguish observed/input facts from suggestions.
- Do not claim to know what a person dreamed or imagined beyond their description.
- Do not claim the output measures intelligence, creativity, mental health, or neurological function.
- Do not claim dream imagery is objectively more accurate than waking imagery.
- Ask one targeted clarification when a missing detail materially changes the scene.

## Output contract
Use JSON-compatible fields:
`objects`, `relations`, `unknowns`, `warnings`, `scores`, and `summary`.
