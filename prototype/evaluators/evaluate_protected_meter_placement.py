from __future__ import annotations
import itertools, json, math
from pathlib import Path

def _expected(task):
    spec=task["public_inputs"]["meter_placement_case"]
    import itertools
    best=None
    for combo in itertools.combinations(spec["candidate_meters"], spec["budget"]):
        covered=[]; weight=0
        for att in spec["attack_vectors"]:
            if any(m in combo for m in att["detectable_by"]): covered.append(att["attack_id"]); weight+=att["risk_weight"]
        cand=(-weight, list(combo), covered)
        if best is None or cand<best: best=cand
    neg,combo,covered=best
    return {"protected_meters":combo,"covered_attack_vectors":covered,"covered_risk_weight":round(-neg,3)}

ALLOWED = set()
TOL=1e-3
def _num(a,b): return math.isclose(float(a),float(b),rel_tol=0,abs_tol=TOL)
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
