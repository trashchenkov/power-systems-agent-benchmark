"""Public surrogate evaluator for PV Volt-VAR inverter control.

The public v0 evaluator uses a deterministic linear voltage-sensitivity model so
it can run without distribution power-flow dependencies. Hidden benchmark cases
can replace the surrogate with pandapower/OpenDSS time-series power flow while
keeping the same submission contract: a monotonic Volt-VAR curve.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


def _load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def _curve_points(submission: dict[str, Any]) -> list[dict[str, float]]:
    raw_curve = submission.get("volt_var_curve", [])
    if not isinstance(raw_curve, list):
        return []
    points: list[dict[str, float]] = []
    for raw in raw_curve:
        try:
            points.append({"voltage_pu": float(raw["voltage_pu"]), "q_fraction": float(raw["q_fraction"])})
        except (KeyError, TypeError, ValueError):
            return []
    return sorted(points, key=lambda item: item["voltage_pu"])


def _interpolate_q_fraction(points: list[dict[str, float]], voltage_pu: float) -> float:
    if voltage_pu <= points[0]["voltage_pu"]:
        return points[0]["q_fraction"]
    if voltage_pu >= points[-1]["voltage_pu"]:
        return points[-1]["q_fraction"]
    for left, right in zip(points, points[1:]):
        if left["voltage_pu"] <= voltage_pu <= right["voltage_pu"]:
            span = right["voltage_pu"] - left["voltage_pu"]
            if span == 0:
                return right["q_fraction"]
            weight = (voltage_pu - left["voltage_pu"]) / span
            return left["q_fraction"] + weight * (right["q_fraction"] - left["q_fraction"])
    return points[-1]["q_fraction"]


def _available_q_kvar(timestep: dict[str, Any]) -> float:
    kva = float(timestep["inverter_kva"])
    kw = float(timestep["pv_kw"])
    return math.sqrt(max(0.0, kva * kva - kw * kw))


def _validate_curve(points: list[dict[str, float]], tolerance: float) -> list[str]:
    violations: list[str] = []
    if len(points) < 2:
        violations.append("volt_var_curve must contain at least two points")
        return violations
    for point in points:
        if not -1.0 <= point["q_fraction"] <= 1.0:
            violations.append("q_fraction must stay within [-1.0, 1.0]")
            break
    for left, right in zip(points, points[1:]):
        if right["voltage_pu"] <= left["voltage_pu"]:
            violations.append("volt_var_curve voltage_pu values must be strictly increasing")
            break
        if right["q_fraction"] > left["q_fraction"] + tolerance:
            violations.append("volt_var_curve must be monotonic non-increasing in q_fraction")
            break
    return violations


def evaluate_case(case: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    limits = case.get("voltage_limits_pu", {})
    v_min = float(limits.get("min", 0.95))
    v_max = float(limits.get("max", 1.05))
    tolerance = float(case.get("monotonic_tolerance", 1e-9))
    points = _curve_points(submission)
    violations = _validate_curve(points, tolerance)

    timeseries: dict[str, dict[str, float]] = {}
    voltage_violation_timesteps: list[str] = []
    q_limit_violations: list[str] = []
    total_control_effort = 0.0

    if points:
        for idx, timestep in enumerate(case.get("timesteps", [])):
            step_id = str(timestep.get("id", f"t{idx}"))
            base_voltage = float(timestep["base_voltage_pu"])
            q_limit = _available_q_kvar(timestep)
            q_fraction = _interpolate_q_fraction(points, base_voltage)
            q_command = q_fraction * q_limit
            if abs(q_fraction) > 1.0 + tolerance:
                q_limit_violations.append(step_id)
            corrected_voltage = base_voltage + float(timestep["voltage_sensitivity_pu_per_kvar"]) * q_command
            timeseries[step_id] = {
                "base_voltage_pu": round(base_voltage, 6),
                "q_available_kvar": round(q_limit, 6),
                "q_fraction": round(q_fraction, 6),
                "q_command_kvar": round(q_command, 6),
                "corrected_voltage_pu": round(corrected_voltage, 6),
            }
            total_control_effort += abs(q_command)
            if corrected_voltage < v_min - 1e-4 or corrected_voltage > v_max + 1e-4:
                voltage_violation_timesteps.append(step_id)

    for step_id in q_limit_violations:
        violations.append(f"q command exceeds inverter capability at {step_id}")
    for step_id in voltage_violation_timesteps:
        violations.append(f"voltage outside limits at {step_id}")

    feasible = not violations
    if feasible:
        effort_penalty = min(20.0, 0.02 * total_control_effort)
        score = max(0.0, 1.0 - effort_penalty / 100.0)
    else:
        score = 0.0

    return {
        "task_id": case.get("task_id"),
        "feasible": feasible,
        "score": round(score, 6),
        "voltage_violation_timesteps": voltage_violation_timesteps,
        "q_limit_violations": q_limit_violations,
        "control_effort_kvar_sum": round(total_control_effort, 6),
        "timeseries": timeseries,
        "violations": violations,
    }


def evaluate_files(case_path: str | Path, submission_path: str | Path) -> dict[str, Any]:
    return evaluate_case(_load_json(case_path), _load_json(submission_path))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate a PV Volt-VAR curve submission.")
    parser.add_argument("case", help="Path to public/hidden case JSON")
    parser.add_argument("submission", help="Path to submission JSON")
    args = parser.parse_args()
    print(json.dumps(evaluate_files(args.case, args.submission), ensure_ascii=False, indent=2))
