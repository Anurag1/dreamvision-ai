"""Cross-model paired benchmark with multiple independent vision judges.

Each image model generates both prompt conditions for each task/repeat.
Every generated image is scored independently by every configured judge.
Human raters receive a blinded CSV template with randomized opaque image IDs.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, os, platform, random, statistics, time
from datetime import datetime, timezone
from pathlib import Path
from dreamvision.engine import analyze_scene
from dreamvision.prompting import direct_prompt, structured_prompt
from dreamvision.multimodal import OpenAIImageProvider, OpenAIVisionJudge

METRICS=("object_fidelity","relation_fidelity","attribute_fidelity","overall_fidelity")

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(dataset, output, image_models, judge_models, repeats=3, size="1024x1024", seed=17):
    tasks=json.loads(Path(dataset).read_text(encoding="utf-8"))
    if not tasks: raise ValueError("Dataset is empty")
    if len(image_models)<2: raise ValueError("Provide at least two image models for cross-model comparison")
    if len(judge_models)<2: raise ValueError("Provide at least two independent judge models")
    out=Path(output); (out/"images").mkdir(parents=True,exist_ok=True)
    rng=random.Random(seed)
    providers={m:OpenAIImageProvider(model=m) for m in image_models}
    judges={m:OpenAIVisionJudge(model=m) for m in judge_models}
    records=[]; blind_rows=[]
    started=datetime.now(timezone.utc).isoformat()
    for image_model in image_models:
      ordered=list(tasks); rng.shuffle(ordered)
      for repeat in range(1,repeats+1):
       for task in ordered:
        parsed=analyze_scene(task["description"])
        conditions=[
          ("direct_baseline",task["description"].strip()),
          ("dreamvision_structured",structured_prompt(task["description"],parsed))
        ]
        rng.shuffle(conditions)
        for condition,prompt in conditions:
          key=f"{task['id']}_{image_model.replace('/','-')}_r{repeat}_{condition}"
          image_path=out/"images"/(key+".png")
          t=time.perf_counter()
          providers[image_model].generate(prompt,image_path,size)
          gen_s=round(time.perf_counter()-t,3)
          opaque=hashlib.sha256(f"{seed}:{key}".encode()).hexdigest()[:12]
          blind_rows.append({"blind_image_id":opaque,"image_path":str(image_path),
             "task_id":task["id"],"repeat":repeat,"image_model":image_model,
             "condition":condition})
          for judge_model,judge in judges.items():
            t=time.perf_counter()
            score=judge.score(image_path,task)
            eval_s=round(time.perf_counter()-t,3)
            records.append({"task_id":task["id"],"repeat":repeat,"image_model":image_model,
              "condition":condition,"judge_model":judge_model,"blind_image_id":opaque,
              "image_path":str(image_path),"prompt_sha256":hashlib.sha256(prompt.encode()).hexdigest(),
              "generation_seconds":gen_s,"evaluation_seconds":eval_s,"scores":score})
    # Raw records retain the condition for analysis; blinded human sheet does not.
    report={"protocol":"cross-image-model, paired prompt conditions, multi-judge",
      "started_at_utc":started,"finished_at_utc":datetime.now(timezone.utc).isoformat(),
      "environment":{"python":platform.python_version(),"platform":platform.platform()},
      "configuration":{"image_models":image_models,"judge_models":judge_models,"repeats":repeats,
        "size":size,"seed":seed,"dataset_sha256":sha(dataset),"dataset_path":str(dataset)},
      "records":records,
      "limitations":["Vision-judge scores are not ground truth.",
        "Model names and access depend on the connected API account.",
        "Generation randomness is not controlled by the ordering seed.",
        "Human ratings are needed for confirmatory conclusions."]}
    (out/"results.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    with (out/"human_ratings_blinded.csv").open("w",newline="",encoding="utf-8") as f:
      w=csv.DictWriter(f,fieldnames=["blind_image_id","object_fidelity_1_to_5",
        "relation_fidelity_1_to_5","attribute_fidelity_1_to_5","overall_fidelity_1_to_5",
        "rater_id_optional","notes"])
      w.writeheader()
      for row in sorted(blind_rows,key=lambda x:x["blind_image_id"]):
       w.writerow({"blind_image_id":row["blind_image_id"]})
    # Key is stored separately; keep it away from blinded rater files.
    (out/"blind_key_restricted.json").write_text(json.dumps(blind_rows,indent=2),encoding="utf-8")
    _write_csv(out/"results.csv",records)
    return report

def _write_csv(path,records):
 import csv
 fields=["task_id","repeat","image_model","condition","judge_model","blind_image_id",
  "image_path","generation_seconds","evaluation_seconds",*METRICS]
 with Path(path).open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
  for r in records:
   w.writerow({**{k:r.get(k) for k in fields if k not in METRICS},
     **{k:r["scores"].get(k) for k in METRICS}})

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--dataset",default="benchmarks/scenes.json")
 p.add_argument("--output",default="benchmark_runs/multimodel-001")
 p.add_argument("--image-models",required=True,help="Comma-separated image model IDs accessible to your API account")
 p.add_argument("--judge-models",required=True,help="Comma-separated vision-capable judge model IDs")
 p.add_argument("--repeats",type=int,default=3); p.add_argument("--size",default="1024x1024")
 p.add_argument("--seed",type=int,default=17)
 a=p.parse_args()
 if not os.getenv("OPENAI_API_KEY"): p.error("OPENAI_API_KEY is required")
 result=run(a.dataset,a.output,[x.strip() for x in a.image_models.split(",") if x.strip()],
   [x.strip() for x in a.judge_models.split(",") if x.strip()],a.repeats,a.size,a.seed)
 print(json.dumps({"records":len(result["records"]),"models":result["configuration"]},indent=2))
 print("Outputs:",a.output)
if __name__=="__main__": main()
