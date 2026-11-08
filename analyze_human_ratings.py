"""Analyze blind human ratings after condition key is unblinded by the study owner."""
import argparse,csv,json,statistics
from collections import defaultdict
from pathlib import Path
METRICS=("object_fidelity_1_to_5","relation_fidelity_1_to_5","attribute_fidelity_1_to_5","overall_fidelity_1_to_5")

def main():
 p=argparse.ArgumentParser()
 p.add_argument("ratings_csv"); p.add_argument("blind_key_json")
 a=p.parse_args()
 key=json.loads(Path(a.blind_key_json).read_text(encoding="utf-8"))
 lookup={x["blind_image_id"]:x for x in key}
 ratings=defaultdict(list)
 with Path(a.ratings_csv).open(newline="",encoding="utf-8") as f:
  for row in csv.DictReader(f):
   bid=row["blind_image_id"]
   if bid not in lookup: raise ValueError(f"Unknown blind_image_id: {bid}")
   vals={}
   for metric in METRICS:
    raw=row.get(metric,"").strip()
    if raw:
     val=float(raw)
     if not 1 <= val <= 5: raise ValueError(f"{metric} must be 1..5")
     vals[metric]=val
   if vals: ratings[bid].append(vals)
 # Average multiple raters per image; preserve number of ratings for audit.
 image_scores={}
 for bid,items in ratings.items():
  image_scores[bid]={m:statistics.mean(x[m] for x in items if m in x)
    for m in METRICS if any(m in x for x in items)}
  image_scores[bid]["n_raters"]=len(items)
 groups=defaultdict(list)
 for bid,score in image_scores.items():
  meta=lookup[bid]
  groups[(meta["image_model"],meta["task_id"],meta["repeat"],meta["condition"])].append(score)
 models=sorted({k[0] for k in groups})
 output={"images_with_human_ratings":len(image_scores),"models":{}}
 for model in models:
  idx={}
  for (im,task,rep,condition),vals in groups.items():
   if im==model:
    # one blinded image id maps to one row; mean ratings across raters above
    idx[(task,rep,condition)]=vals[0]
  paired=[]
  for task,rep in sorted({(t,r) for (t,r,c) in idx}):
   a0=idx.get((task,rep,"direct_baseline")); b0=idx.get((task,rep,"dreamvision_structured"))
   if a0 and b0: paired.append((a0,b0))
  result={"n_paired_task_repeats":len(paired),"mean_paired_differences":{}}
  for metric in METRICS:
   diffs=[b[metric]-a1[metric] for a1,b in paired if metric in a1 and metric in b]
   if diffs:
    result["mean_paired_differences"][metric]={
     "dreamvision_minus_direct":round(statistics.mean(diffs),3),
     "median":round(statistics.median(diffs),3),
     "per_pair": [round(x,3) for x in diffs]}
  output["models"][model]=result
 print(json.dumps(output,indent=2))
if __name__=="__main__":main()
