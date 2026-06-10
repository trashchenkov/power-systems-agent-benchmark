"""Evaluator for compact islanded microgrid P/Q dispatch."""
from __future__ import annotations
import json, math
from pathlib import Path
from typing import Any

def _load_json(path: Path) -> dict[str, Any]: return json.loads(path.read_text(encoding="utf-8"))
def _round(x): return round(float(x), 3)

def solve_core(task):
    c=task["islanded_pq_case"]; load_p=float(c["load"]["p_mw"]); load_q=float(c["load"]["q_mvar"])
    inv=c["inverter"]; diesel=c["diesel"]
    p_inv=min(float(inv["p_available_mw"]), load_p-float(diesel["pmin_mw"]))
    p_diesel=load_p-p_inv
    q_need=load_q
    s=float(inv["s_rating_mva"]); q_inv_cap=math.sqrt(max(0.0, s*s-p_inv*p_inv))
    q_inv=max(-q_inv_cap, min(q_inv_cap, q_need-float(diesel["q_preferred_mvar"])))
    q_diesel=q_need-q_inv
    v=float(c["voltage_model"]["base_voltage_pu"])+float(c["voltage_model"]["sensitivity_pu_per_mvar"])*(q_inv+q_diesel)
    cost=p_diesel*float(diesel["variable_cost_per_h"])+abs(q_diesel-float(diesel["q_preferred_mvar"]))*float(diesel["q_deviation_penalty_per_mvar_h"])
    return {"dispatch":{"diesel":{"p_mw":_round(p_diesel),"q_mvar":_round(q_diesel)},"inverter":{"p_mw":_round(p_inv),"q_mvar":_round(q_inv)}},"voltage_pu":_round(v),"total_cost":_round(cost)}

def solve_case(task):
    out=solve_core(task); out["rationale"]="Used available inverter active power, allocated reactive power within capability, and balanced islanded P/Q demand."; return out

def _num(v,n,viol):
    try: x=float(v)
    except (TypeError,ValueError): viol.append(f"{n} must be numeric"); return None
    if not math.isfinite(x): viol.append(f"{n} must be finite"); return None
    return x

def _close(n,a,e,viol,tol=0.01):
    if a is not None and abs(a-e)>tol: viol.append(f"{n}={a:.6g} differs from expected {e:.6g}")

def evaluate_case(task, submission):
    viol=[]; allowed={"dispatch","voltage_pu","total_cost","rationale"}; extra=sorted(set(submission)-allowed)
    if extra: viol.append(f"unknown answer fields: {extra}")
    exp=solve_core(task); disp=submission.get("dispatch")
    if not isinstance(disp,dict): viol.append("dispatch must be an object"); disp={}
    for unit in ["diesel","inverter"]:
        obj=disp.get(unit)
        if not isinstance(obj,dict): viol.append(f"missing dispatch.{unit}"); obj={}
        for k,e in exp["dispatch"][unit].items(): _close(f"dispatch.{unit}.{k}", _num(obj.get(k),f"dispatch.{unit}.{k}",viol), e, viol)
    _close("voltage_pu", _num(submission.get("voltage_pu"),"voltage_pu",viol), exp["voltage_pu"], viol)
    _close("total_cost", _num(submission.get("total_cost"),"total_cost",viol), exp["total_cost"], viol)
    return {"task_id":task["task_id"],"feasible":not viol,"score":1.0 if not viol else 0.0,"study":exp,"violations":viol}

def evaluate(task_path: Path, submission_path: Path): return evaluate_case(_load_json(task_path), _load_json(submission_path))
def main(argv=None):
    import argparse; p=argparse.ArgumentParser(); p.add_argument('task',type=Path); p.add_argument('submission',type=Path); a=p.parse_args(argv); print(json.dumps(evaluate(a.task,a.submission),ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
