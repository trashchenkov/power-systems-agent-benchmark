"""Evaluator for critical clearing time from public stability sweep data."""
from __future__ import annotations
import json, math
from pathlib import Path
TOL=1e-3
ALLOWED={"critical_clearing_time_s","limiting_case","stable_times_s","unstable_times_s","rationale"}

def _round(x, nd=3): return round(float(x)+0.0, nd)
def _expected(task):
    spec=task["public_inputs"]["stability_sweep"]
    cases=spec["cases"]
    stable=[]; unstable=[]
    for c in cases:
        ok=bool(c["stable"] and c["max_rotor_angle_deg"] <= spec["max_angle_deg"] and c["min_voltage_pu"] >= spec["min_voltage_pu"])
        (stable if ok else unstable).append(c)
    if not stable: cct=0.0; limiting="none"
    else:
        last=max(stable, key=lambda c:c["clearing_time_s"])
        cct=last["clearing_time_s"]; limiting=last["case_id"]
    return {"critical_clearing_time_s":_round(cct),"limiting_case":limiting,"stable_times_s":[_round(c["clearing_time_s"]) for c in stable],"unstable_times_s":[_round(c["clearing_time_s"]) for c in unstable]}

def _num(a,b,tol=TOL): return math.isclose(float(a), float(b), rel_tol=0, abs_tol=tol)
def evaluate_case(task, submission):
    exp=_expected(task); violations=[]
    extra=set(submission)-ALLOWED
    if extra: violations.append(f"unknown answer fields: {sorted(extra)}")
    for k in ["critical_clearing_time_s"]:
        if k not in submission or not _num(submission[k], exp[k]): violations.append(f"{k} expected {exp[k]} got {submission.get(k)}")
    for k in ["limiting_case","stable_times_s","unstable_times_s"]:
        if submission.get(k)!=exp[k]: violations.append(f"{k} expected {exp[k]} got {submission.get(k)}")
    return {"task_id":task.get("task_id"),"feasible":not violations,"score":1.0 if not violations else 0.0,"study":exp,"violations":violations}
def main():
    import sys
    task=json.loads(Path(sys.argv[1]).read_text()); sub=json.loads(Path(sys.argv[2]).read_text())
    print(json.dumps(evaluate_case(task, sub), indent=2))
if __name__=="__main__": main()
