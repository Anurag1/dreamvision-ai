"""Optional OpenAI-backed image generation and vision evaluation adapters."""
from __future__ import annotations
import base64
import json
import mimetypes
from pathlib import Path
from typing import Any

class OpenAIImageProvider:
    def __init__(self, api_key: str | None = None, model: str = "gpt-image-1"):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install optional dependencies: pip install -r requirements.txt") from exc
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, prompt: str, output_path: str | Path, size: str = "1024x1024") -> dict[str, Any]:
        response = self.client.images.generate(model=self.model, prompt=prompt, size=size)
        item = response.data[0]
        if not getattr(item, "b64_json", None):
            raise RuntimeError("Image API did not return b64_json; URL-only responses are not persisted by this adapter")
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(base64.b64decode(item.b64_json))
        return {"path": str(path), "model": self.model, "size": size}

class OpenAIVisionJudge:
    """Score one generated image against task constraints using a vision-capable model."""
    def __init__(self, api_key: str | None = None, model: str = "gpt-4o"):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install optional dependencies: pip install -r requirements.txt") from exc
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def score(self, image_path: str | Path, task: dict[str, Any]) -> dict[str, Any]:
        path = Path(image_path)
        mime = mimetypes.guess_type(path.name)[0] or "image/png"
        data_url = f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"
        rubric = {"task": task["description"], "required_objects": task.get("required_objects", []),
                  "required_relations": task.get("required_relations", []),
                  "required_attributes": task.get("required_attributes", [])}
        response = self.client.chat.completions.create(
            model=self.model, temperature=0, response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": (
                    "You are a strict visual benchmark evaluator. Judge only what is visible. "
                    "Do not infer invisible facts. Return JSON with integer scores 0-5 for "
                    "object_fidelity, relation_fidelity, attribute_fidelity, and overall_fidelity; "
                    "also return concise evidence and missing_or_wrong_items. 0 means absent/wrong, "
                    "5 means clearly satisfied. Be conservative."
                )},
                {"role": "user", "content": [
                    {"type": "text", "text": "Evaluate this image against this benchmark specification:\n" + json.dumps(rubric)},
                    {"type": "image_url", "image_url": {"url": data_url}}
                ]}
            ])
        result = json.loads(response.choices[0].message.content or "{}")
        for key in ("object_fidelity", "relation_fidelity", "attribute_fidelity", "overall_fidelity"):
            value = result.get(key)
            if not isinstance(value, (int, float)) or not 0 <= value <= 5:
                raise ValueError(f"Judge returned invalid {key}: {value!r}")
        result["judge_model"] = self.model
        return result
