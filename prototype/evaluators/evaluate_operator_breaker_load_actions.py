from __future__ import annotations
import itertools, json, math
from pathlib import Path

def _expected(task):
    spec=task["public_inputs"]["operator_action_case"]
    branches={b["branch_id"]:b.copy() for b in spec["branches"]}
    best=None
    import itertools
    actions=spec["candidate_actions"]
    for r in range(spec["max_actions"]+1):
        for combo in itertools.combinations(actions,r):
            flows={k:v["base_flow_mw"] for k,v in branches.items()}; shed=0; opened=[]
            for a in combo:
                if a["type"]=="open_breaker": opened.append(a["branch_id"]); flows[a["branch_id"]]=0
                elif a["type"]=="shed_load": shed+=a["mw"]; 
                for bid,delta in a.get("flow_delta_mw",{}).items(): flows[bid]=flows.get(bid,0)+delta
            overload=sum(max(0,abs(flows[bid])-branches[bid]["limit_mw"]) for bid in branches)
            if overload<=1e-9 and shed<=spec["max_shed_mw"]:
                score=shed+0.1*len(combo); cand=(score,shed,[a["action_id"] for a in combo],flows)
                if best is None or cand<best: best=cand
    score,shed,ids,flows=best
    return {"selected_actions":ids,"load_shed_mw":round(shed,3),"post_action_flows_mw":{k:round(v,3) for k,v in flows.items()},"all_limits_satisfied":True}

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
    for k,v in exp.items(): _cmp(k, submission.get(k), v, violations)
    return {"task_id":task.get("task_id"),"feasible":not violations,"score":1.0 if not violations else 0.0,"study":exp,"violations":violations}
def main():
    import sys
    task=json.loads(Path(sys.argv[1]).read_text()); sub=json.loads(Path(sys.argv[2]).read_text())
    print(json.dumps(evaluate_case(task, sub), indent=2))
if __name__=="__main__": main()
