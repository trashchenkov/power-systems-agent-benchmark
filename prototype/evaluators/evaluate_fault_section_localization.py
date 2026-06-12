"""Evaluator for fault-section localization from FCI states and outage complaints."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

ALLOWED_EXTRA = {"rationale"}
TOL = 1e-6

def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def _path_to_source(node: str, parent: dict[str, str]) -> list[str]:
    path=[node]
    while node in parent:
        node=parent[node]
        path.append(node)
    return list(reversed(path))

def solve_case(task: dict[str, Any]) -> dict[str, Any]:
    case=task["fault_localization_case"]
    sections=case["sections"]
    nodes=case["nodes"]
    parent={v["to"]: v["from"] for v in sections.values()}
    section_by_child={v["to"]: sid for sid,v in sections.items()}
    fci_states=case["observed_fci_state"]
    complaints=set(case["outage_complaint_nodes"])
    scores=[]
    for sid,sec in sections.items():
        fault_child=sec["to"]
        fault_path=set(_path_to_source(fault_child,parent))
        expected_fci={f: (case["fci_locations"][f] in fault_path) for f in case["fci_locations"]}
        fci_mismatch=sum(1 for f,state in fci_states.items() if bool(state)!=expected_fci[f])
        # downstream customers of the candidate faulted section are de-energized.
        downstream=set()
        stack=[fault_child]
        children={n:[] for n in nodes}
        for s in sections.values(): children[s["from"]].append(s["to"])
        while stack:
            n=stack.pop(); downstream.add(n); stack.extend(children.get(n,[]))
        complaint_missed=len(complaints-downstream)
        complaint_extra=len((downstream & set(case["customer_nodes"]))-complaints)
        score=fci_mismatch*10+complaint_missed*3+complaint_extra
        scores.append((score,sid,sorted(downstream & set(case["customer_nodes"]))))
    scores.sort(key=lambda x:(x[0],x[1]))
    _,best,affected=scores[0]
    return {"faulted_section": best, "affected_customer_nodes": affected}

def _close(a: Any,b: Any,tol: float=TOL)->bool:
    try: return abs(float(a)-float(b))<=tol
    except Exception: return False

def evaluate_case(task: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    expected=solve_case(task); violations=[]
    allowed=set(expected)|ALLOWED_EXTRA
    extra=sorted(set(submission)-allowed)
    if extra: violations.append(f"unknown answer fields: {extra}")
    if submission.get("faulted_section")!=expected["faulted_section"]:
        violations.append(f"faulted_section expected {expected['faulted_section']!r}, got {submission.get('faulted_section')!r}")
    _aff=submission.get("affected_customer_nodes")
    if sorted(_aff if isinstance(_aff, list) else [])!=expected["affected_customer_nodes"]:
        violations.append(f"affected_customer_nodes expected {expected['affected_customer_nodes']!r}, got {submission.get('affected_customer_nodes')!r}")
    feasible=not violations
    return {"task_id": task.get("task_id"), "feasible": feasible, "score": 1.0 if feasible else 0.0, "study": expected, "violations": violations}

def evaluate(task_path: str | Path, submission_path: str | Path) -> dict[str, Any]:
    return evaluate_case(_load_json(task_path), _load_json(submission_path))

if __name__ == "__main__":
    import sys
    print(json.dumps(evaluate(sys.argv[1], sys.argv[2]), indent=2, ensure_ascii=False))
