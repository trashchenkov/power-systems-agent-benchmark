"""Evaluator for scenario dispatch under renewable uncertainty."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _times(case: dict[str, Any]) -> list[str]:
    return case["time_periods"]


def _max_net_load(case: dict[str, Any], t: str) -> float:
    vals = []
    for s in case["scenarios"]:
        vals.append(float(s["load_mw"][t]) - float(s["renewable_mw"][t]))
    return max(vals)


def _cost(case: dict[str, Any], dispatch: dict[str, dict[str, float]]) -> float:
    total = 0.0
    for g in case["generators"]:
        gid = g["id"]
        for t in _times(case):
            total += float(dispatch[gid][t]) * float(g["variable_cost_per_mwh"])
    return total


def solve_dispatch(task: dict[str, Any]) -> dict[str, Any]:
    case = task["dispatch_uncertainty_case"]
    times = _times(case)
    gens = sorted(case["generators"], key=lambda g: float(g["variable_cost_per_mwh"]))
    dispatch = {g["id"]: {} for g in case["generators"]}
    margins: dict[str, float] = {}
    reserve = float(case["reserve_requirement_mw"])
    for t in times:
        requirement = _max_net_load(case, t) + reserve
        remaining = requirement
        for g in gens:
            gid = g["id"]
            val = min(float(g["pmax_mw"]), max(float(g["pmin_mw"]), remaining)) if remaining > 0 else float(g["pmin_mw"])
            dispatch[gid][t] = round(val, 3)
            remaining -= val
        # If the cheapest-first pmin assignment over-produced, reduce the most expensive generator down to pmin.
        total = sum(dispatch[g["id"]][t] for g in case["generators"])
        excess = total - requirement
        for g in sorted(case["generators"], key=lambda x: float(x["variable_cost_per_mwh"]), reverse=True):
            if excess <= 1e-9:
                break
            gid = g["id"]
            reducible = dispatch[gid][t] - float(g["pmin_mw"])
            delta = min(reducible, excess)
            dispatch[gid][t] = round(dispatch[gid][t] - delta, 3)
            excess -= delta
        supply = sum(dispatch[g["id"]][t] for g in case["generators"])
        margins[t] = round(supply - _max_net_load(case, t), 3)
    return {
        "dispatch_mw": dispatch,
        "worst_case_margin_mw": margins,
        "total_cost": round(_cost(case, dispatch), 3),
    }


def solve_case(task: dict[str, Any]) -> dict[str, Any]:
    s = solve_dispatch(task)
    return {
        "dispatch_mw": s["dispatch_mw"],
        "worst_case_margin_mw": s["worst_case_margin_mw"],
        "total_cost": s["total_cost"],
        "rationale": "Scheduled generators against the maximum net-load scenario at each time while preserving the required reserve and minimizing variable cost."
    }


def _num(value: Any, name: str, violations: list[str]) -> float | None:
    try:
        x = float(value)
    except (TypeError, ValueError):
        violations.append(f"{name} must be numeric")
        return None
    if not math.isfinite(x):
        violations.append(f"{name} must be finite")
        return None
    return x


def _close(name: str, actual: float | None, expected: float, violations: list[str], abs_tol: float = 0.01) -> None:
    if actual is None:
        return
    if abs(actual - expected) > abs_tol:
        violations.append(f"{name}={actual:.6g} differs from expected {expected:.6g} by more than {abs_tol}")


def _extract_dispatch(case: dict[str, Any], submission: dict[str, Any], violations: list[str]) -> dict[str, dict[str, float]]:
    submitted = submission.get("dispatch_mw")
    if not isinstance(submitted, dict):
        violations.append("dispatch_mw must be an object keyed by generator id")
        submitted = {}
    out: dict[str, dict[str, float]] = {}
    for g in case["generators"]:
        gid = g["id"]
        obj = submitted.get(gid)
        if not isinstance(obj, dict):
            violations.append(f"missing dispatch object for generator {gid}")
            obj = {}
        out[gid] = {}
        for t in _times(case):
            val = _num(obj.get(t), f"dispatch_mw.{gid}.{t}", violations)
            if val is None:
                continue
            out[gid][t] = val
            if val < float(g["pmin_mw"]) - 1e-9 or val > float(g["pmax_mw"]) + 1e-9:
                violations.append(f"dispatch_mw.{gid}.{t} violates generator bounds")
    return out


def evaluate_case(task: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    violations: list[str] = []
    allowed = {"dispatch_mw", "worst_case_margin_mw", "total_cost", "rationale"}
    extra = sorted(set(submission) - allowed)
    if extra:
        violations.append(f"unknown answer fields: {extra}")
    case = task["dispatch_uncertainty_case"]
    expected = solve_dispatch(task)
    dispatch = _extract_dispatch(case, submission, violations)
    reserve = float(case["reserve_requirement_mw"])
    if not violations:
        for t in _times(case):
            supply = sum(dispatch[g["id"]][t] for g in case["generators"])
            margin = supply - _max_net_load(case, t)
            if margin + 1e-9 < reserve:
                violations.append(f"worst-case reserve margin at {t} is {margin:.6g}, below required {reserve}")
            submitted_margin = None
            if isinstance(submission.get("worst_case_margin_mw"), dict):
                submitted_margin = _num(submission["worst_case_margin_mw"].get(t), f"worst_case_margin_mw.{t}", violations)
            else:
                violations.append("worst_case_margin_mw must be an object keyed by time period")
            _close(f"worst_case_margin_mw.{t}", submitted_margin, expected["worst_case_margin_mw"][t], violations)
        for gid, by_t in expected["dispatch_mw"].items():
            for t, exp in by_t.items():
                _close(f"dispatch_mw.{gid}.{t}", dispatch[gid][t], exp, violations)
        _close("total_cost", _num(submission.get("total_cost"), "total_cost", violations), expected["total_cost"], violations)
    feasible = not violations
    return {"task_id": task["task_id"], "feasible": feasible, "score": 1.0 if feasible else 0.0, "study": expected, "violations": violations}


def evaluate(task_path: Path, submission_path: Path) -> dict[str, Any]:
    return evaluate_case(_load_json(task_path), _load_json(submission_path))


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("task", type=Path)
    parser.add_argument("submission", type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(evaluate(args.task, args.submission), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
