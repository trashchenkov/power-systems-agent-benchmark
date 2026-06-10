"""Evaluator for power-quality event classification from RMS traces."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def classify_event(task: dict[str, Any]) -> dict[str, Any]:
    case = task["power_quality_case"]
    rules = case["classification_rules"]
    trace = case["rms_trace"]
    nominal = float(case.get("nominal_voltage_pu", 1.0))
    sag_low = float(rules["sag_lower_pu"])
    sag_high = float(rules["sag_upper_pu"])
    interruption = float(rules["interruption_upper_pu"])
    swell = float(rules["swell_lower_pu"])
    event_rows = []
    labels = []
    for row in trace:
        v = float(row["voltage_pu"])
        label = "normal"
        if v < interruption:
            label = "interruption"
        elif sag_low <= v < sag_high:
            label = "voltage_sag"
        elif v > swell:
            label = "voltage_swell"
        labels.append(label)
        if label != "normal":
            event_rows.append(row)
    if not event_rows:
        event_class = "normal"
        start = end = None
        duration = 0.0
    else:
        non_normal = [label for label in labels if label != "normal"]
        event_class = max(sorted(set(non_normal)), key=non_normal.count)
        start = event_rows[0]["timestamp_ms"]
        end = event_rows[-1]["timestamp_ms"]
        step_ms = float(case["sample_interval_ms"])
        duration = (float(end) - float(start) + step_ms) / 1000.0
    voltages = [float(r["voltage_pu"]) for r in trace]
    currents = [float(r["current_pu"]) for r in trace]
    severity = nominal - min(voltages) if event_class == "voltage_sag" else max(voltages) - nominal
    return {
        "event_class": event_class,
        "start_timestamp_ms": start,
        "end_timestamp_ms": end,
        "duration_s": round(duration, 6),
        "min_voltage_pu": round(min(voltages), 6),
        "max_voltage_pu": round(max(voltages), 6),
        "max_current_pu": round(max(currents), 6),
        "severity_pu": round(severity, 6),
    }


def solve_case(task: dict[str, Any]) -> dict[str, Any]:
    e = classify_event(task)
    return {
        "event_class": e["event_class"],
        "start_timestamp_ms": e["start_timestamp_ms"],
        "end_timestamp_ms": e["end_timestamp_ms"],
        "duration_s": e["duration_s"],
        "min_voltage_pu": e["min_voltage_pu"],
        "max_current_pu": e["max_current_pu"],
        "rationale": "Classified the contiguous non-normal RMS-voltage interval using the published sag/swell/interruption thresholds."
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


def _close(name: str, actual: float | None, expected: float, violations: list[str], abs_tol: float = 0.001) -> None:
    if actual is None:
        return
    if abs(actual - expected) > abs_tol:
        violations.append(f"{name}={actual:.6g} differs from expected {expected:.6g} by more than {abs_tol}")


def evaluate_case(task: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    violations: list[str] = []
    allowed = {"event_class", "start_timestamp_ms", "end_timestamp_ms", "duration_s", "min_voltage_pu", "max_current_pu", "rationale"}
    extra = sorted(set(submission) - allowed)
    if extra:
        violations.append(f"unknown answer fields: {extra}")
    expected = classify_event(task)
    for key in ["event_class", "start_timestamp_ms", "end_timestamp_ms"]:
        if submission.get(key) != expected[key]:
            violations.append(f"{key} must be {expected[key]}")
    for key in ["duration_s", "min_voltage_pu", "max_current_pu"]:
        _close(key, _num(submission.get(key), key, violations), expected[key], violations)
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
