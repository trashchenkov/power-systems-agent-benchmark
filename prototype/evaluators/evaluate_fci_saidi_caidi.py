"""Evaluator for SAIDI/CAIDI impact of FCI deployment."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

ALLOWED_EXTRA={"rationale"}; TOL=1e-3

def _load_json(path: str | Path) -> dict[str, Any]: return json.loads(Path(path).read_text(encoding="utf-8"))
def _close(a: Any,b: Any,tol: float=TOL)->bool:
    try: return abs(float(a)-float(b))<=tol
    except Exception: return False

def _indices(case: dict[str, Any], use_fci: bool) -> dict[str, float]:
    total=float(case["total_customers"])
    cmin=0.0; cint=0.0
    deployed=set(case["deployed_fci_locations"])
    for sid,f in case["fault_sections"].items():
        rate=float(f["annual_fault_rate"]); cust=float(f["customers_interrupted"]); dur=float(f["base_restoration_minutes"])
        if use_fci:
            best=max([float(case["fci_locations"][loc]["restoration_time_reduction_min"].get(sid,0.0)) for loc in deployed] or [0.0])
            dur=max(float(case["minimum_restoration_minutes"]), dur-best)
        cmin += rate*cust*dur
        cint += rate*cust
    saidi=cmin/total
    caidi=cmin/cint if cint else 0.0
    saifi=cint/total
    return {"saidi_min_per_customer_year": round(saidi,3), "caidi_min_per_interruption": round(caidi,3), "saifi_interruptions_per_customer_year": round(saifi,4)}

def solve_case(task: dict[str, Any]) -> dict[str, Any]:
    case=task["fci_reliability_case"]
    base=_indices(case,False); withf=_indices(case,True)
    return {"baseline": base, "with_fci": withf, "saidi_improvement_min_per_customer_year": round(base["saidi_min_per_customer_year"]-withf["saidi_min_per_customer_year"],3), "caidi_improvement_min_per_interruption": round(base["caidi_min_per_interruption"]-withf["caidi_min_per_interruption"],3)}

def evaluate_case(task: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    expected=solve_case(task); violations=[]; allowed=set(expected)|ALLOWED_EXTRA
    extra=sorted(set(submission)-allowed)
    if extra: violations.append(f"unknown answer fields: {extra}")
    for group in ["baseline","with_fci"]:
        got=submission.get(group,{})
        for k,v in expected[group].items():
            if not _close(got.get(k), v): violations.append(f"{group}.{k} expected {v}, got {got.get(k)}")
    for k in ["saidi_improvement_min_per_customer_year","caidi_improvement_min_per_interruption"]:
        if not _close(submission.get(k), expected[k]): violations.append(f"{k} expected {expected[k]}, got {submission.get(k)}")
    feasible=not violations
    return {"task_id": task.get("task_id"), "feasible": feasible, "score": 1.0 if feasible else 0.0, "study": expected, "violations": violations}

def evaluate(task_path: str | Path, submission_path: str | Path) -> dict[str, Any]: return evaluate_case(_load_json(task_path), _load_json(submission_path))
if __name__ == "__main__":
    import sys; print(json.dumps(evaluate(sys.argv[1], sys.argv[2]), indent=2, ensure_ascii=False))
