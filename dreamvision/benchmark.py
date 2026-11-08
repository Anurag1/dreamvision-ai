"""Reproducible paired benchmark: direct prompt vs DreamVision structured prompt."""
from __future__ import annotations
import hashlib
import json
import platform
import random
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .engine import analyze_scene
from .prompting import direct_prompt, structured_prompt

def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def run_benchmark(dataset_path: str, output_dir: str, image_model: str, judge_model: str,
                  repeats: int = 1, size: str = "1024x1024", seed: int = 17) -> dict[str, Any]:
    """Run live provider calls. Requires OPENAI_API_KEY and the optional openai package."""
    from .multimodal import OpenAIImageProvider, OpenAIVisionJudge
    tasks = json.loads(Path(dataset_path).read_text(encoding="utf-8"))
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("Dataset must be a non-empty JSON list")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    image_provider = OpenAIImageProvider(model=image_model)
    judge = OpenAIVisionJudge(model=judge_model)
    rng = random.Random(seed)
    records = []
    started = datetime.now(timezone.utc).isoformat()
    for repeat in range(repeats):
        ordered = list(tasks)
        rng.shuffle(ordered)
        for task in ordered:
            analysis = analyze_scene(task["description"])
            conditions = {"direct_baseline": direct_prompt(task["description"]),
                          "dreamvision_structured": structured_prompt(task["description"], analysis)}
            condition_items = list(conditions.items())
            rng.shuffle(condition_items)
            for condition, prompt in condition_items:
                stem = f"{task['id']}_r{repeat + 1}_{condition}"
                image_path = out / "images" / f"{stem}.png"
                tick = time.perf_counter()
                image_provider.generate(prompt, image_path, size=size)
                generation_seconds = round(time.perf_counter() - tick, 3)
                tick = time.perf_counter()
                score = judge.score(image_path, task)
                evaluation_seconds = round(time.perf_counter() - tick, 3)
                records.append({"task_id": task["id"], "repeat": repeat + 1, "condition": condition,
                    "description": task["description"], "prompt_sha256": sha256_text(prompt),
                    "prompt": prompt, "image_path": str(image_path), "image_model": image_model,
                    "image_size": size, "generation_seconds": generation_seconds,
                    "evaluation_seconds": evaluation_seconds, "scores": score})
    score_keys = ("object_fidelity", "relation_fidelity", "attribute_fidelity", "overall_fidelity")
    summary = {}
    for condition in ("direct_baseline", "dreamvision_structured"):
        rows = [r for r in records if r["condition"] == condition]
        summary[condition] = {key: round(statistics.mean(r["scores"][key] for r in rows), 3)
                              for key in score_keys}
        summary[condition]["n_images"] = len(rows)
    report = {"benchmark": "DreamVision paired prompt benchmark",
        "started_at_utc": started, "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {"python": platform.python_version(), "platform": platform.platform(),
                        "openai_package": _package_version("openai")},
        "configuration": {"image_model": image_model, "judge_model": judge_model, "size": size,
            "repeats": repeats, "seed": seed, "dataset_path": str(dataset_path),
            "dataset_sha256": hashlib.sha256(Path(dataset_path).read_bytes()).hexdigest()},
        "summary": summary, "records": records,
        "interpretation_warning": "Judge-model scores are model-based evaluations, not human ratings. Use independent judges and human evaluation before efficacy claims."}
    (out / "results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    _write_csv(out / "results.csv", records)
    return report

def _write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    import csv
    fields = ["task_id", "repeat", "condition", "image_model", "judge_model", "image_path",
              "generation_seconds", "evaluation_seconds", "object_fidelity", "relation_fidelity",
              "attribute_fidelity", "overall_fidelity"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in records:
            scores = row["scores"]
            writer.writerow({"task_id": row["task_id"], "repeat": row["repeat"],
                "condition": row["condition"], "image_model": row["image_model"],
                "judge_model": scores.get("judge_model"), "image_path": row["image_path"],
                "generation_seconds": row["generation_seconds"], "evaluation_seconds": row["evaluation_seconds"],
                **{key: scores[key] for key in fields[8:]}})

def _package_version(name: str) -> str | None:
    try:
        from importlib.metadata import version
        return version(name)
    except Exception:
        return None
