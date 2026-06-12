"""Evaluator for EN 50160-style voltage compliance on a compact time series."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def compute_compliance(task: dict[str, Any]) -> dict[str, Any]:
    case = task["voltage_compliance_case"]
    rules = case["rules"]
    series = case["voltage_series_pu"]
    nominal = float(case.get("nominal_voltage_pu", 1.0))
    lower_95 = nominal + float(rules["normal_lower_deviation_pu"])
    upper_95 = nominal + float(rules["normal_upper_deviation_pu"])
    lower_abs = nominal + float(rules["absolute_lower_deviation_pu"])
    upper_abs = nominal + float(rules["absolute_upper_deviation_pu"])
    min_required = float(rules["minimum_percent_within_normal_band"])
    values = [float(row["voltage_pu"]) for row in series]
    normal = [row["timestamp"] for row, v in zip(series, values) if lower_95 <= v <= upper_95]
    below = [row["timestamp"] for row, v in zip(series, values) if v < lower_95]
    above = [row["timestamp"] for row, v in zip(series, values) if v > upper_95]
    absolute_violations = [row["timestamp"] for row, v in zip(series, values) if v < lower_abs or v > upper_abs]
    pct = 100.0 * len(normal) / len(series)
    compliant = pct >= min_required and not absolute_violations
    mitigation = case["mitigation_options"]
    # Tap change is an additive pu shift in this compact public case.
    best = None
    for tap in mitigation["candidate_tap_changes_pu"]:
        shifted = [v + float(tap) for v in values]
        n = sum(1 for v in shifted if lower_95 <= v <= upper_95)
        abs_bad = sum(1 for v in shifted if v < lower_abs or v > upper_abs)
        score = (n, -abs_bad, -abs(float(tap)))
        if best is None or score > best[0]:
            best = (score, float(tap), shifted)
    assert best is not None
    best_tap = best[1]
    shifted = best[2]
    mitigated_pct = 100.0 * sum(1 for v in shifted if lower_95 <= v <= upper_95) / len(shifted)
    mitigated_abs_bad = [series[i]["timestamp"] for i, v in enumerate(shifted) if v < lower_abs or v > upper_abs]
    return {
        "compliant": compliant,
        "percent_within_normal_band": round(pct, 3),
        "min_voltage_pu": round(min(values), 6),
        "max_voltage_pu": round(max(values), 6),
        "below_normal_timestamps": below,
        "above_normal_timestamps": above,
        "absolute_violation_timestamps": absolute_violations,
        "recommended_tap_change_pu": round(best_tap, 6),
        "mitigated_percent_within_normal_band": round(mitigated_pct, 3),
        "mitigated_absolute_violation_timestamps": mitigated_abs_bad,
    }


def solve_case(task: dict[str, Any]) -> dict[str, Any]:
    s = compute_compliance(task)
    return {
        "compliant": s["compliant"],
        "percent_within_normal_band": s["percent_within_normal_band"],
        "min_voltage_pu": s["min_voltage_pu"],
        "max_voltage_pu": s["max_voltage_pu"],
        "below_normal_timestamps": s["below_normal_timestamps"],
        "above_normal_timestamps": s["above_normal_timestamps"],
        "recommended_tap_change_pu": s["recommended_tap_change_pu"],
        "rationale": "Checked the share of 10-minute voltages inside the normal band, absolute voltage limits, and selected the best listed tap correction."
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
    allowed = {"compliant", "percent_within_normal_band", "min_voltage_pu", "max_voltage_pu", "below_normal_timestamps", "above_normal_timestamps", "recommended_tap_change_pu", "rationale"}
    extra = sorted(set(submission) - allowed)
    if extra:
        violations.append(f"unknown answer fields: {extra}")
    expected = compute_compliance(task)
    if submission.get("compliant") is not expected["compliant"]:
        violations.append(f"compliant must be {expected['compliant']}")
    for key in ["percent_within_normal_band", "min_voltage_pu", "max_voltage_pu", "recommended_tap_change_pu"]:
        _close(key, _num(submission.get(key), key, violations), expected[key], violations)
    for key in ["below_normal_timestamps", "above_normal_timestamps"]:
        _got = submission.get(key)
        if sorted(_got if isinstance(_got, list) else []) != sorted(expected[key]):
            violations.append(f"{key} must be {expected[key]}")
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
