from __future__ import annotations
import itertools, json, math
from pathlib import Path

def _expected(task):
    spec=task["public_inputs"]["mas_handover_case"]
    freq=spec["frequency_hz"]; nominal=spec["nominal_hz"]
    state="emergency" if abs(freq-nominal)>=spec["emergency_deviation_hz"] else ("alert" if abs(freq-nominal)>=spec["alert_deviation_hz"] else "normal")
    candidates=[]
    for a in spec["agents"]:
        headroom=a["pmax_mw"]-a["current_mw"] if freq<nominal else a["current_mw"]-a["pmin_mw"]
        if a["available"] and headroom>=spec["min_headroom_mw"] and a["latency_ms"]<=spec["max_latency_ms"]:
            candidates.append(( -headroom, a["latency_ms"], a["agent_id"], round(headroom,3)))
    candidates.sort(); lead=candidates[0]
    return {"frequency_state":state,"lead_agent":lead[2],"handover_required":spec["current_lead_agent"]!=lead[2],"lead_headroom_mw":lead[3]}

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
