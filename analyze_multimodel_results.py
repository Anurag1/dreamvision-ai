"""Summarize paired prompt effects separately by image model and judge model."""
import argparse,json,random,statistics
from pathlib import Path
METRICS=("object_fidelity","relation_fidelity","attribute_fidelity","overall_fidelity")

def main():
 p=argparse.ArgumentParser()
 p.add_argument("results"); p.add_argument("--bootstrap",type=int,default=5000); p.add_argument("--seed",type=int,default=2026)
 a=p.parse_args(); data=json.loads(Path(a.results).read_text())
 rows=data["records"]; groups={}
 for r in rows:
  groups.setdefault((r["image_model"],r["judge_model"]),[]).append(r)
 out={"paired_effects_by_image_model_and_judge":{},"bootstrap_replicates":a.bootstrap,"bootstrap_seed":a.seed}
 for (im,jm),rs in sorted(groups.items()):
  idx={(r["task_id"],r["repeat"],r["condition"]):r for r in rs}; paired=[]
  keys={(r["task_id"],r["repeat"]) for r in rs}
  for task,rep in sorted(keys):
   x=idx.get((task,rep,"direct_baseline")); y=idx.get((task,rep,"dreamvision_structured"))
   if x and y: paired.append((x,y))
  result={"n_paired":len(paired),"metrics":{}}
  for metric in METRICS:
   d=[y["scores"][metric]-x["scores"][metric] for x,y in paired]
   if not d: continue
   rng=random.Random(a.seed)
   boot=sorted(statistics.mean(d[rng.randrange(len(d))] for _ in d) for _ in range(a.bootstrap))
   result["metrics"][metric]={"mean_difference":round(statistics.mean(d),3),
    "median_difference":round(statistics.median(d),3),
    "bootstrap_95_percentile_interval":[round(boot[int(.025*len(boot))],3),
      round(boot[min(len(boot)-1,int(.975*len(boot)))],3)],
    "task_repeat_differences":[round(v,3) for v in d]}
  out["paired_effects_by_image_model_and_judge"][f"{im} | {jm}"]=result
 print(json.dumps(out,indent=2))
if __name__=="__main__":main()
