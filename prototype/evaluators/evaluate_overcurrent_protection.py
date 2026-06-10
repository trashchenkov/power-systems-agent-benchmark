"""Deterministic evaluator for line overcurrent protection settings."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def _range_violation(value: float, limits: dict[str, Any], name: str, unit: str) -> str | None:
    min_value = float(limits["min"])
    max_value = float(limits["max"])
    if value < min_value:
        return f"{name} below minimum {min_value:.6f} {unit}"
    if value > max_value:
        return f"{name} above maximum {max_value:.6f} {unit}"
    return None


def evaluate_case(case: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    violations: list[str] = []
    pickup = float(submission.get("pickup_current_a", 0.0))
    time_delay = float(submission.get("time_delay_s", 0.0))

    max_load = float(case["max_load_current_a"])
    min_fault = float(case["min_fault_current_a"])
    ct_ratio = float(case["ct_ratio_primary_per_secondary"])
    load_margin = float(case.get("load_margin_multiplier", 1.2))
    min_sensitivity = float(case.get("min_sensitivity_factor", 1.5))
    downstream_delay = float(case.get("downstream_time_delay_s", 0.0))
    selectivity_margin = float(case.get("selectivity_margin_s", 0.3))

    min_pickup = max_load * load_margin
    sensitivity = min_fault / pickup if pickup > 0.0 else 0.0
    secondary_pickup = pickup / ct_ratio if ct_ratio > 0.0 else 0.0
    min_time_delay = downstream_delay + selectivity_margin

    if pickup < min_pickup:
        violations.append(f"pickup_current_a below load margin minimum {min_pickup:.6f} A")
    if sensitivity < min_sensitivity:
        violations.append(
            f"sensitivity factor {sensitivity:.6f} below minimum {min_sensitivity:.6f}"
        )
    if time_delay < min_time_delay:
        violations.append(f"time_delay_s below selectivity minimum {min_time_delay:.6f} s")

    secondary_violation = _range_violation(
        secondary_pickup,
        case.get("relay_secondary_pickup_range_a", {"min": 0.0, "max": float("inf")}),
        "secondary_pickup_a",
        "A",
    )
    if secondary_violation:
        violations.append(secondary_violation)

    time_violation = _range_violation(
        time_delay,
        case.get("time_delay_range_s", {"min": 0.0, "max": float("inf")}),
        "time_delay_s",
        "s",
    )
    if time_violation:
        violations.append(time_violation)

    feasible = not violations
    if feasible:
        pickup_slack = max(0.0, pickup - min_pickup)
        time_slack = max(0.0, time_delay - min_time_delay)
        # Prefer lower pickup/time settings that still satisfy load, sensitivity,
        # and selectivity. Keep the score simple and stable for public smoke tests.
        score = max(0.0, 1.0 - (pickup_slack / max(min_pickup, 1.0) * 10.0 + time_slack * 5.0) / 100.0)
    else:
        score = 0.0

    return {
        "task_id": case.get("task_id"),
        "feasible": feasible,
        "score": round(score, 6),
        "pickup_current_a": round(pickup, 6),
        "time_delay_s": round(time_delay, 6),
        "min_pickup_current_a": round(min_pickup, 6),
        "min_time_delay_s": round(min_time_delay, 6),
        "sensitivity_factor": round(sensitivity, 6),
        "secondary_pickup_a": round(secondary_pickup, 6),
        "violations": violations,
    }


def evaluate_files(case_path: str | Path, submission_path: str | Path) -> dict[str, Any]:
    return evaluate_case(_load_json(case_path), _load_json(submission_path))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate an overcurrent-protection setting submission.")
    parser.add_argument("case", help="Path to public/hidden case JSON")
    parser.add_argument("submission", help="Path to submission JSON")
    args = parser.parse_args()
    print(json.dumps(evaluate_files(args.case, args.submission), ensure_ascii=False, indent=2))
