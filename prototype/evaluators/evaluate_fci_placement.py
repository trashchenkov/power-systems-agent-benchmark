"""Evaluator for FCI placement to reduce expected patrol time."""
from __future__ import annotations
import itertools, json
from pathlib import Path
from typing import Any

ALLOWED_EXTRA={"rationale"}
TOL=1e-6

def _load_json(path: str | Path) -> dict[str, Any]: return json.loads(Path(path).read_text(encoding="utf-8"))
def _close(a: Any,b: Any,tol: float=TOL)->bool:
    try: return abs(float(a)-float(b))<=tol
    except Exception: return False

def _value(case: dict[str, Any], selected: tuple[str,...]) -> tuple[float, dict[str,float]]:
    gains={sid:0.0 for sid in case["fault_sections"]}
    for sid, fault in case["fault_sections"].items():
        best=0.0
        for loc in selected:
            best=max(best, float(case["candidate_locations"][loc]["section_gain_minutes"].get(sid,0.0)))
        gains[sid]=best
    expected=sum(float(case["fault_sections"][sid]["annual_fault_rate"])*float(case["fault_sections"][sid]["customers_interrupted"])*gain for sid,gain in gains.items())
    return expected, gains

def solve_case(task: dict[str, Any]) -> dict[str, Any]:
    case=task["fci_placement_case"]; budget=int(case["budget"])
    candidates=sorted(case["candidate_locations"])
    best=None
    for comb in itertools.combinations(candidates,budget):
        value,gains=_value(case,comb)
        item=(-value, comb, gains)
        if best is None or item<best: best=item
    value=-best[0]; selected=list(best[1]); gains=best[2]
    return {"selected_locations": selected, "expected_customer_minutes_saved": round(value,3), "section_patrol_time_reduction_min": {k: round(v,3) for k,v in gains.items()}}

def evaluate_case(task: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    expected=solve_case(task); violations=[]; allowed=set(expected)|ALLOWED_EXTRA
    extra=sorted(set(submission)-allowed)
    if extra: violations.append(f"unknown answer fields: {extra}")
    _sel=submission.get("selected_locations")
    if sorted(_sel if isinstance(_sel, list) else [])!=expected["selected_locations"]:
        violations.append(f"selected_locations expected {expected['selected_locations']!r}, got {submission.get('selected_locations')!r}")
    if not _close(submission.get("expected_customer_minutes_saved"), expected["expected_customer_minutes_saved"], 1e-3):
        violations.append(f"expected_customer_minutes_saved expected {expected['expected_customer_minutes_saved']}, got {submission.get('expected_customer_minutes_saved')}")
    got=submission.get("section_patrol_time_reduction_min")
    got=got if isinstance(got,dict) else {}
    for sid,val in expected["section_patrol_time_reduction_min"].items():
        if not _close(got.get(sid), val, 1e-3): violations.append(f"section_patrol_time_reduction_min.{sid} expected {val}, got {got.get(sid)}")
    feasible=not violations
    return {"task_id": task.get("task_id"), "feasible": feasible, "score": 1.0 if feasible else 0.0, "study": expected, "violations": violations}

def evaluate(task_path: str | Path, submission_path: str | Path) -> dict[str, Any]: return evaluate_case(_load_json(task_path), _load_json(submission_path))
if __name__ == "__main__":
    import sys; print(json.dumps(evaluate(sys.argv[1], sys.argv[2]), indent=2, ensure_ascii=False))
