"""Evaluator for compact rolling-horizon microgrid dispatch."""
from __future__ import annotations
import itertools, json, math
from pathlib import Path
from typing import Any

def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def _times(case): return case["time_periods"]
def _round(x): return round(float(x), 3)

def _simulate(case, battery):
    soc=float(case["battery"]["initial_soc_mwh"]); rows={}; feasible=True
    for t,b in zip(_times(case), battery):
        load=float(case["load_mw"][t]); pv=float(case["pv_mw"][t])
        # b > 0 discharges into AC bus; b < 0 charges.
        if b >= 0: soc -= b*case["interval_hours"]/float(case["battery"]["discharge_efficiency"])
        else: soc -= b*case["interval_hours"]*float(case["battery"]["charge_efficiency"])
        net = load - pv - b
        g = max(float(case["generator"]["pmin_mw"]), min(float(case["generator"]["pmax_mw"]), net))
        curtail = max(0.0, pv + b + g - load)
        shed = max(0.0, load - pv - b - g)
        if soc < float(case["battery"]["soc_min_mwh"])-1e-9 or soc > float(case["battery"]["soc_max_mwh"])+1e-9 or shed>1e-9:
            feasible=False
        rows[t]={"diesel_mw":_round(g),"battery_mw":_round(b),"pv_curtailment_mw":_round(curtail),"soc_mwh":_round(soc),"shed_mw":_round(shed)}
    cost=sum(rows[t]["diesel_mw"]*case["interval_hours"]*float(case["generator"]["variable_cost_per_mwh"]) for t in _times(case))
    return feasible, _round(cost), rows

def solve_core(task):
    case=task["rolling_microgrid_dispatch_case"]
    b=case["battery"]; step=float(b["dispatch_step_mw"])
    vals=[]; x=-float(b["charge_pmax_mw"])
    while x <= float(b["discharge_pmax_mw"])+1e-9:
        vals.append(round(x,6)); x+=step
    best=None
    for combo in itertools.product(vals, repeat=len(_times(case))):
        feas,cost,rows=_simulate(case, combo)
        if not feas: continue
        key=(cost, sum(abs(v) for v in combo), combo)
        if best is None or key < best[0]: best=(key,cost,rows)
    if best is None: raise ValueError("no feasible dispatch")
    return {"dispatch":best[2], "total_cost":best[1]}

def solve_case(task):
    out=solve_core(task)
    return {"dispatch":out["dispatch"],"total_cost":out["total_cost"],"rationale":"Enumerated feasible rolling battery setpoints and selected the least-cost diesel schedule."}

def _num(v,name,viol):
    try: x=float(v)
    except (TypeError,ValueError): viol.append(f"{name} must be numeric"); return None
    if not math.isfinite(x): viol.append(f"{name} must be finite"); return None
    return x

def _close(name,a,e,viol,tol=0.01):
    if a is None: return
    if abs(a-e)>tol: viol.append(f"{name}={a:.6g} differs from expected {e:.6g}")

def evaluate_case(task, submission):
    viol=[]; allowed={"dispatch","total_cost","rationale"}
    extra=sorted(set(submission)-allowed)
    if extra: viol.append(f"unknown answer fields: {extra}")
    exp=solve_core(task); subd=submission.get("dispatch")
    if not isinstance(subd, dict): viol.append("dispatch must be an object keyed by timestamp"); subd={}
    for t,row in exp["dispatch"].items():
        got=subd.get(t)
        if not isinstance(got, dict): viol.append(f"missing dispatch object for {t}"); got={}
        for k,e in row.items(): _close(f"dispatch.{t}.{k}", _num(got.get(k),f"dispatch.{t}.{k}",viol), e, viol)
    _close("total_cost", _num(submission.get("total_cost"),"total_cost",viol), exp["total_cost"], viol)
    return {"task_id":task["task_id"],"feasible":not viol,"score":1.0 if not viol else 0.0,"study":exp,"violations":viol}

def evaluate(task_path: Path, submission_path: Path): return evaluate_case(_load_json(task_path), _load_json(submission_path))
def main(argv=None):
    import argparse; p=argparse.ArgumentParser(); p.add_argument('task',type=Path); p.add_argument('submission',type=Path); a=p.parse_args(argv); print(json.dumps(evaluate(a.task,a.submission),ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
