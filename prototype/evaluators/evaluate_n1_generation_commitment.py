from __future__ import annotations
import itertools, json, math
from pathlib import Path

def _expected(task):
    spec=task["public_inputs"]["commitment_case"]
    units=spec["units"]; demand=spec["demand_mw"]
    import itertools
    best=None
    for r in range(1,len(units)+1):
        for combo in itertools.combinations(units,r):
            cap=sum(u["pmax_mw"] for u in combo)
            n1_cap=cap-max(u["pmax_mw"] for u in combo)
            reserve=cap-demand
            if cap>=demand and n1_cap>=demand and reserve>=spec["reserve_mw"]:
                cost=sum(u["startup_cost_usd"] for u in combo)+sum(u["no_load_cost_usd"] for u in combo)
                ids=[u["unit_id"] for u in combo]
                cand=(cost, len(ids), ids, cap, n1_cap, reserve)
                if best is None or cand<best: best=cand
    cost,_,ids,cap,n1,rv=best
    return {"committed_units":ids,"available_capacity_mw":round(cap,3),"n1_secure_capacity_mw":round(n1,3),"reserve_mw":round(rv,3),"commitment_cost_usd":round(cost,3)}

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

def evaluate_case(task, submission):
    exp=_expected(task); allowed=set(exp)|{"rationale"}; violations=[]
    extra=set(submission)-allowed
    if extra: violations.append(f"unknown answer fields: {sorted(extra)}")
    for k,v in exp.items():
        if k=="committed_units":
            # The committed set is order-independent: any ordering of the same
            # units is the same commitment decision.
            got=submission.get(k)
            if not isinstance(got, list) or sorted(map(str,got))!=sorted(map(str,v)):
                violations.append(f"committed_units expected {sorted(v)} got {sorted(got) if isinstance(got,list) else got}")
        else:
            _cmp(k, submission.get(k), v, violations)
    return {"task_id":task.get("task_id"),"feasible":not violations,"score":1.0 if not violations else 0.0,"study":exp,"violations":violations}
def main():
    import sys
    task=json.loads(Path(sys.argv[1]).read_text()); sub=json.loads(Path(sys.argv[2]).read_text())
    print(json.dumps(evaluate_case(task, sub), indent=2))
if __name__=="__main__": main()
