"""Evaluator for compact microgrid economic dispatch."""
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
    case=task["microgrid_dispatch_case"]
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
    return {"dispatch":out["dispatch"],"total_cost":out["total_cost"],"rationale":"Enumerated feasible battery setpoints and selected the least-cost diesel schedule."}

def _num(v,name,viol):
    try: x=float(v)
    except (TypeError,ValueError): viol.append(f"{name} must be numeric"); return None
    if not math.isfinite(x): viol.append(f"{name} must be finite"); return None
    return x

def _close(name,a,e,viol,tol=0.01):
    if a is None: return
    if abs(a-e)>tol: viol.append(f"{name}={a:.6g} differs from expected {e:.6g}")

CASE_KEY="microgrid_dispatch_case"

def evaluate_case(task, submission):
    # The battery profile is the only true decision variable: diesel, SOC,
    # curtailment, and shedding all follow deterministically from it. The
    # submitted schedule is therefore re-simulated and judged on feasibility
    # and cost gap against the enumerated optimum, so alternative equal-cost
    # optima are accepted.
    viol=[]; allowed={"dispatch","total_cost","rationale"}
    extra=sorted(set(submission)-allowed)
    if extra: viol.append(f"unknown answer fields: {extra}")
    case=task[CASE_KEY]
    exp=solve_core(task)
    subd=submission.get("dispatch")
    cost=None
    if not isinstance(subd, dict):
        viol.append("dispatch must be an object keyed by timestamp")
    else:
        battery=[]
        for t in _times(case):
            row=subd.get(t)
            if not isinstance(row, dict): viol.append(f"missing dispatch object for {t}"); break
            b=_num(row.get("battery_mw"), f"dispatch.{t}.battery_mw", viol)
            if b is None: break
            battery.append(b)
        else:
            feas, cost, rows=_simulate(case, battery)
            if not feas:
                viol.append("submitted battery schedule violates SOC bounds or sheds load")
            for t in _times(case):
                got=subd[t]
                for k,e in rows[t].items():
                    _close(f"dispatch.{t}.{k}", _num(got.get(k),f"dispatch.{t}.{k}",viol), e, viol, tol=0.05)
            _close("total_cost", _num(submission.get("total_cost"),"total_cost",viol), cost, viol, tol=0.5)
    feasible=not viol
    if not feasible:
        score=0.0; gap=None
    else:
        gap=round(max(0.0, cost-exp["total_cost"]),3)
        score=1.0 if gap<=0.01 else round(max(0.0, 1.0-gap/exp["total_cost"]),6)
    return {"task_id":task["task_id"],"feasible":feasible,"score":score,"cost_gap_usd":gap,"optimal_cost":exp["total_cost"],"study":exp,"violations":viol}

def evaluate(task_path: Path, submission_path: Path): return evaluate_case(_load_json(task_path), _load_json(submission_path))
def main(argv=None):
    import argparse; p=argparse.ArgumentParser(); p.add_argument('task',type=Path); p.add_argument('submission',type=Path); a=p.parse_args(argv); print(json.dumps(evaluate(a.task,a.submission),ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
