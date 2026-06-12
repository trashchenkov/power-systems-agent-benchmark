
from __future__ import annotations
import json, math, itertools
from pathlib import Path
from typing import Any
ALLOWED_EXTRA={"rationale"}
def _load_json(path: str|Path)->dict[str,Any]: return json.loads(Path(path).read_text(encoding="utf-8"))
def _close(a,b,tol=1e-3):
    try: return abs(float(a)-float(b))<=tol
    except Exception: return False

def _quantile(xs,q):
    xs=sorted(xs); pos=(len(xs)-1)*q; lo=math.floor(pos); hi=math.ceil(pos)
    if lo==hi: return xs[lo]
    return xs[lo]*(hi-pos)+xs[hi]*(pos-lo)
def solve_case(task):
    c=task["pv_lcoe_case"]; crf=float(c["capital_recovery_factor"]); size=float(c["system_size_kw_dc"]); energy=float(c["annual_energy_mwh_year1"]); fixed=float(c["fixed_om_usd_per_kw_year"])*size
    vals={}
    for sid,s in c["soft_cost_scenarios"].items():
        capex=size*(float(c["hard_cost_usd_per_kw"])+sum(float(c["soft_cost_components_usd_per_kw"][k])*float(mult) for k,mult in s.items()))
        lcoe=(capex*crf+fixed)/energy
        vals[sid]=round(lcoe,3)
    arr=list(vals.values())
    return {"scenario_lcoe_usd_per_mwh": vals, "lcoe_quantiles_usd_per_mwh": {"p10": round(_quantile(arr,0.10),3), "p50": round(_quantile(arr,0.50),3), "p90": round(_quantile(arr,0.90),3)}, "expected_lcoe_usd_per_mwh": round(sum(arr)/len(arr),3)}
def evaluate_case(task, submission):
    exp=solve_case(task); violations=[]; allowed=set(exp)|ALLOWED_EXTRA
    extra=sorted(set(submission)-allowed)
    if extra: violations.append(f"unknown answer fields: {extra}")
    _scen=submission.get("scenario_lcoe_usd_per_mwh"); _scen=_scen if isinstance(_scen,dict) else {}
    for sid,v in exp["scenario_lcoe_usd_per_mwh"].items():
        if not _close(_scen.get(sid),v): violations.append(f"scenario_lcoe_usd_per_mwh.{sid} expected {v}, got {_scen.get(sid)!r}")
    _qs=submission.get("lcoe_quantiles_usd_per_mwh"); _qs=_qs if isinstance(_qs,dict) else {}
    for q,v in exp["lcoe_quantiles_usd_per_mwh"].items():
        if not _close(_qs.get(q),v): violations.append(f"lcoe_quantiles_usd_per_mwh.{q} expected {v}, got {_qs.get(q)!r}")
    if not _close(submission.get("expected_lcoe_usd_per_mwh"), exp["expected_lcoe_usd_per_mwh"]): violations.append("expected_lcoe_usd_per_mwh mismatch")
    return {"task_id":task.get("task_id"),"feasible":not violations,"score":1.0 if not violations else 0.0,"study":exp,"violations":violations}
def evaluate(task_path, submission_path): return evaluate_case(_load_json(task_path), _load_json(submission_path))
if __name__=='__main__':
 import sys; print(json.dumps(evaluate(sys.argv[1],sys.argv[2]),indent=2,ensure_ascii=False))
