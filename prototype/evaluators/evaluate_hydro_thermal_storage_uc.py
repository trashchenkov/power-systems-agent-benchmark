from __future__ import annotations
import itertools, json, math
from pathlib import Path

def _expected(task):
    spec=task["public_inputs"]["uc_case"]
    units={u["unit_id"]: u for u in spec["thermal_units"]}
    thermal={}; emissions=0.0; cost=0.0
    for h in spec["hours"]:
        demand=h["load_mw"]-h["hydro_mw"]-h["storage_discharge_mw"]
        # Merit-order dispatch with gas only for residual above coal's useful capacity.
        gas_p=max(0.0, demand-units["coal"]["pmax_mw"])
        if gas_p>0: gas_p=max(gas_p, units["gas"]["pmin_mw"])
        coal_p=demand-gas_p
        dispatch={"coal": round(coal_p,3)}
        if gas_p>0: dispatch["gas"]=round(gas_p,3)
        thermal[h["hour_id"]]=dispatch
        for uid,p in dispatch.items():
            cost += p*units[uid]["cost_usd_per_mwh"]
            emissions += p*units[uid]["emission_ton_per_mwh"]
    return {"thermal_dispatch_mw":thermal,"total_cost_usd":round(cost,3),"emissions_ton":round(emissions,3),"emission_cap_satisfied":emissions <= spec["emission_cap_ton"]}

ALLOWED = set()
TOL=1e-3
def _num(a,b):
    try:
        return math.isclose(float(a), float(b),rel_tol=0,abs_tol=TOL)
    except (TypeError, ValueError):
        return False
def _cmp(path, got, exp, violations):
    if isinstance(exp, dict):
        if not isinstance(got, dict): violations.append(f"{path} expected object got {type(got).__name__}"); return
        if set(got)!=set(exp): violations.append(f"{path} keys expected {sorted(exp)} got {sorted(got)}")
        for k,v in exp.items(): _cmp(f"{path}.{k}", got.get(k), v, violations)
    elif isinstance(exp, list):
        if got!=exp: violations.append(f"{path} expected {exp} got {got}")
    elif isinstance(exp, (int,float)) and not isinstance(exp,bool):
        if got is None or not _num(got, exp): violations.append(f"{path} expected {exp} got {got}")
    else:
        if got!=exp: violations.append(f"{path} expected {exp} got {got}")

def _drop_zero_dispatch(submission):
    """Treat explicit zero-MW entries as equivalent to omitting the unit."""
    dispatch=submission.get("thermal_dispatch_mw")
    if not isinstance(dispatch, dict): return submission
    cleaned=dict(submission)
    cleaned["thermal_dispatch_mw"]={
        hour: {uid: p for uid, p in row.items() if not (isinstance(p,(int,float)) and abs(float(p))<1e-9)}
        if isinstance(row, dict) else row
        for hour, row in dispatch.items()
    }
    return cleaned

def evaluate_case(task, submission):
    exp=_expected(task); allowed=set(exp)|{"rationale"}; violations=[]
    submission=_drop_zero_dispatch(submission)
    extra=set(submission)-allowed
    if extra: violations.append(f"unknown answer fields: {sorted(extra)}")
    for k,v in exp.items(): _cmp(k, submission.get(k), v, violations)
    return {"task_id":task.get("task_id"),"feasible":not violations,"score":1.0 if not violations else 0.0,"study":exp,"violations":violations}
def main():
    import sys
    task=json.loads(Path(sys.argv[1]).read_text()); sub=json.loads(Path(sys.argv[2]).read_text())
    print(json.dumps(evaluate_case(task, sub), indent=2))
if __name__=="__main__": main()
