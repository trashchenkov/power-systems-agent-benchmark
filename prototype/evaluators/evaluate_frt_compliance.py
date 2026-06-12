"""Public surrogate evaluator for grid-code fault ride-through compliance.

The v0 evaluator checks a voltage/time ride-through envelope and a coarse
reactive-current support rule over an event trace. Hidden variants can use exact
standard clauses or dynamic simulation traces while preserving the pass/fail
submission contract.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def _required_voltage(curve: list[dict[str, Any]], duration_s: float) -> float:
    for point in sorted(curve, key=lambda item: float(item["max_duration_s"])):
        if duration_s <= float(point["max_duration_s"]):
            return float(point["min_voltage_pu"])
    return float(curve[-1]["min_voltage_pu"])


def evaluate_case(case: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    trace = sorted(case.get("event_trace", []), key=lambda item: float(item["time_s"]))
    curve = case.get("ride_through_curve", [])
    req = case.get("reactive_current_requirement", {})
    violations: list[str] = []

    if not trace:
        violations.append("event_trace must be non-empty")
    if not curve:
        violations.append("ride_through_curve must be non-empty")

    ride_through_pass = True
    reactive_current_pass = True
    sag_start: float | None = None
    min_voltage = min((float(point.get("voltage_pu", 1.0)) for point in trace), default=1.0)
    max_duration = 0.0

    if trace and curve:
        for point in trace:
            time_s = float(point["time_s"])
            voltage = float(point["voltage_pu"])
            connected = bool(point.get("connected", True))
            if voltage < 0.999 and sag_start is None:
                sag_start = time_s
            if sag_start is None:
                continue
            duration = time_s - sag_start
            max_duration = max(max_duration, duration)
            required_voltage = _required_voltage(curve, duration)
            inside_envelope = voltage >= required_voltage
            if inside_envelope and not connected:
                ride_through_pass = False
                violations.append(f"disconnected inside ride-through envelope at {time_s:.6f} s")
                break

    voltage_below = float(req.get("voltage_below_pu", 0.9))
    min_iq = float(req.get("min_iq_pu", 0.0))
    deadline = float(req.get("response_deadline_s", 0.0))
    sag_trigger: float | None = None
    for point in trace:
        voltage = float(point.get("voltage_pu", 1.0))
        time_s = float(point.get("time_s", 0.0))
        if voltage <= voltage_below and sag_trigger is None:
            sag_trigger = time_s
        if sag_trigger is not None and voltage <= voltage_below and time_s - sag_trigger >= deadline:
            if float(point.get("iq_pu", 0.0)) < min_iq:
                reactive_current_pass = False
                violations.append(f"reactive current support below {min_iq:.6f} pu after deadline")
                break

    declared_raw = submission.get("declared_compliant")
    if not isinstance(declared_raw, bool):
        # The verdict is the agent's answer: a missing or non-boolean field is
        # an agent failure, never a default pass.
        violations.append(f"declared_compliant must be a boolean, got {declared_raw!r}")
    declared = declared_raw is True
    feasible = not violations and declared
    if not declared and not violations:
        violations.append("submission declares non-compliance for a compliant trace")
        feasible = False
    score = 1.0 if feasible else 0.0
    return {
        "task_id": case.get("task_id"),
        "feasible": feasible,
        "score": score,
        "ride_through_pass": ride_through_pass,
        "reactive_current_pass": reactive_current_pass,
        "min_voltage_pu": round(min_voltage, 6),
        "max_event_duration_s": round(max_duration, 6),
        "violations": violations,
    }


def evaluate_files(case_path: str | Path, submission_path: str | Path) -> dict[str, Any]:
    return evaluate_case(_load_json(case_path), _load_json(submission_path))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate an FRT/grid-code compliance report.")
    parser.add_argument("case", help="Path to public/hidden case JSON")
    parser.add_argument("submission", help="Path to submission JSON")
    args = parser.parse_args()
    print(json.dumps(evaluate_files(args.case, args.submission), ensure_ascii=False, indent=2))
