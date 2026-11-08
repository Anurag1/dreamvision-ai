"""Exploratory factor analysis: which scene properties benefit from graph prompting?

Reports per-image-model and per-judge paired differences against direct prompting,
stratified by annotated scene factors. These are descriptive subgroup results,
not causal proof; scene-level replication is required.
"""
import argparse,json,statistics
from collections import defaultdict
from pathlib import Path
METRICS=("object_fidelity","relation_fidelity","attribute_fidelity","overall_fidelity")
ARMS=("objects_only","relations_only","graph_full")

def main():
 p=argparse.ArgumentParser()
 p.add_argument("results")
 a=p.parse_args()
 data=json.loads(Path(a.results).read_text(encoding="utf-8"))
 records=data["records"]
 # One score per task/repeat/model/condition/judge.
 index={}
 for r in records:
  index[(r["image_model"],r["judge_model"],r["task_id"],r["repeat"],r["condition"])]=r
 strata=defaultdict(lambda:defaultdict(list))
 for (im,jm,task,rep,condition),r in index.items():
  if condition=="direct_baseline": continue
  base=index.get((im,jm,task,rep,"direct_baseline"))
  if not base: continue
  factors=r.get("factors") or base.get("factors") or {}
  for factor,value in factors.items():
   strata[(im,jm,condition,factor,str(value))]["_n"].append(1)
   for metric in METRICS:
    strata[(im,jm,condition,factor,str(value))][metric].append(
      r["scores"][metric]-base["scores"][metric])
 output={"interpretation":"Positive means this prompt arm scored higher than direct prompting. Small subgroup counts are exploratory.",
         "subgroups":[]}
 for key,values in sorted(strata.items()):
  im,jm,arm,factor,level=key
  item={"image_model":im,"judge_model":jm,"prompt_arm":arm,
        "factor":factor,"level":level,"n_task_repeats":len(values["_n"]),"effects":{}}
  for metric in METRICS:
   d=values.get(metric,[])
   if d:
    item["effects"][metric]={"mean_difference":round(statistics.mean(d),3),
       "median_difference":round(statistics.median(d),3)}
  output["subgroups"].append(item)
 print(json.dumps(output,indent=2))
if __name__=="__main__":main()
