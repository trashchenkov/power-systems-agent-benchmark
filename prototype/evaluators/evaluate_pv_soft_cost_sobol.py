
from __future__ import annotations
import json, math, itertools
from pathlib import Path
from typing import Any
ALLOWED_EXTRA={"rationale"}
def _load_json(path: str|Path)->dict[str,Any]: return json.loads(Path(path).read_text(encoding="utf-8"))
def _close(a,b,tol=1e-3):
    try: return abs(float(a)-float(b))<=tol
    except Exception: return False

def _model(c, x):
    base=float(c["base_soft_cost_usd_per_kw"]); y=base
    for k,val in x.items(): y += float(c["linear_effect_usd_per_kw"][k])*val
    for pair,coef in c.get("interaction_effect_usd_per_kw",{}).items():
        a,b=pair.split("*"); y += float(coef)*x[a]*x[b]
    return y
def solve_case(task):
    c=task["pv_soft_cost_sobol_case"]; vars=list(c["variables"])
    combos=[dict(zip(vars,bits)) for bits in itertools.product([0,1], repeat=len(vars))]
    ys=[_model(c,x) for x in combos]; mean=sum(ys)/len(ys); var=sum((y-mean)**2 for y in ys)/len(ys)
    first={}; total={}
    for varname in vars:
        means=[]
        for val in [0,1]:
            subset=[_model(c,x) for x in combos if x[varname]==val]; means.append(sum(subset)/len(subset))
        first[varname]=round(sum((m-mean)**2 for m in means)/len(means)/var,4)
        # total = E Var(Y | X_-i) / Var(Y)
        groups={}
        for x in combos:
            key=tuple((k,x[k]) for k in vars if k!=varname); groups.setdefault(key,[]).append(_model(c,x))
        total[varname]=round(sum(sum((y-sum(g)/len(g))**2 for y in g)/len(g) for g in groups.values())/len(groups)/var,4)
    ranking=sorted(vars, key=lambda k:(-first[k], k))
    return {"first_order_indices": first, "total_order_indices": total, "sensitivity_ranking": ranking, "output_variance": round(var,3)}
def evaluate_case(task, submission):
    exp=solve_case(task); violations=[]; allowed=set(exp)|ALLOWED_EXTRA
    extra=sorted(set(submission)-allowed)
    if extra: violations.append(f"unknown answer fields: {extra}")
    if submission.get("sensitivity_ranking")!=exp["sensitivity_ranking"]: violations.append(f"sensitivity_ranking expected {exp['sensitivity_ranking']}, got {submission.get('sensitivity_ranking')}")
    for group in ["first_order_indices","total_order_indices"]:
        for k,v in exp[group].items():
            if not _close(submission.get(group,{}).get(k),v,1e-4): violations.append(f"{group}.{k} expected {v}, got {submission.get(group,{}).get(k)}")
    if not _close(submission.get("output_variance"), exp["output_variance"]): violations.append("output_variance mismatch")
    return {"task_id":task.get("task_id"),"feasible":not violations,"score":1.0 if not violations else 0.0,"study":exp,"violations":violations}
def evaluate(task_path, submission_path): return evaluate_case(_load_json(task_path), _load_json(submission_path))
if __name__=='__main__':
 import sys; print(json.dumps(evaluate(sys.argv[1],sys.argv[2]),indent=2,ensure_ascii=False))
