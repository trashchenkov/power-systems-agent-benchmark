"""Evaluator for short-circuit current, breaker rating, and relay pickup selection."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

SQRT3 = math.sqrt(3.0)


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _z(value: dict[str, Any]) -> complex:
    return complex(float(value.get("r_ohm", 0.0)), float(value.get("x_ohm", 0.0)))


def compute_fault_study(task: dict[str, Any]) -> dict[str, Any]:
    case = task["short_circuit_case"]
    v_ll_v = float(case["voltage_kv"]) * 1000.0
    source = _z(case["source_thevenin_impedance"])
    transformer = _z(case["transformer_impedance"])
    feeder = case["feeder"]
    z_per_km = complex(float(feeder["r_ohm_per_km"]), float(feeder["x_ohm_per_km"]))
    faults = []
    max_3ph_ka = 0.0
    min_2ph_ka = float("inf")
    for loc in case["fault_locations"]:
        distance = float(loc["distance_km"])
        z_total = source + transformer + z_per_km * distance
        i3_ka = v_ll_v / (SQRT3 * abs(z_total)) / 1000.0
        # Simple balanced approximation: line-to-line fault current is sqrt(3)/2 of 3-phase current.
        i2_ka = (SQRT3 / 2.0) * i3_ka
        faults.append({"id": loc["id"], "distance_km": distance, "i3ph_ka": round(i3_ka, 6), "i2ph_ka": round(i2_ka, 6)})
        max_3ph_ka = max(max_3ph_ka, i3_ka)
        min_2ph_ka = min(min_2ph_ka, i2_ka)
    load_current_a = float(case["max_load_current_a"])
    rules = case["selection_rules"]
    min_breaker = max_3ph_ka * float(rules["breaker_safety_factor"])
    ratings = [float(x) for x in case["available_breaker_interrupting_ratings_ka"]]
    selected_breaker = next((rating for rating in sorted(ratings) if rating >= min_breaker), None)
    min_pickup_a = load_current_a * float(rules["relay_load_margin"])
    max_pickup_a = (min_2ph_ka * 1000.0) / float(rules["minimum_fault_sensitivity"])
    return {
        "faults": faults,
        "max_3ph_fault_ka": round(max_3ph_ka, 6),
        "min_2ph_fault_ka": round(min_2ph_ka, 6),
        "minimum_breaker_rating_ka": round(min_breaker, 6),
        "selected_breaker_rating_ka": selected_breaker,
        "relay_pickup_min_a": round(min_pickup_a, 6),
        "relay_pickup_max_a": round(max_pickup_a, 6),
    }


def solve_nominal_selection(task: dict[str, Any]) -> dict[str, Any]:
    study = compute_fault_study(task)
    pickup = round((study["relay_pickup_min_a"] + study["relay_pickup_max_a"]) / 2.0, 3)
    return {
        "max_3ph_fault_ka": study["max_3ph_fault_ka"],
        "min_2ph_fault_ka": study["min_2ph_fault_ka"],
        "breaker_interrupting_rating_ka": study["selected_breaker_rating_ka"],
        "relay_pickup_a_primary": pickup,
        "rationale": "Computed near/far short-circuit currents from Thevenin, transformer, and feeder impedances; selected the smallest breaker rating above the safety margin and a pickup between load margin and minimum-fault sensitivity limits."
    }


def _num(submission: dict[str, Any], key: str, violations: list[str]) -> float | None:
    if key not in submission:
        violations.append(f"missing required field: {key}")
        return None
    try:
        value = float(submission[key])
    except (TypeError, ValueError):
        violations.append(f"{key} must be numeric")
        return None
    if not math.isfinite(value):
        violations.append(f"{key} must be finite")
        return None
    return value


def evaluate_case(task: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    study = compute_fault_study(task)
    violations: list[str] = []
    max_fault = _num(submission, "max_3ph_fault_ka", violations)
    min_fault = _num(submission, "min_2ph_fault_ka", violations)
    breaker = _num(submission, "breaker_interrupting_rating_ka", violations)
    pickup = _num(submission, "relay_pickup_a_primary", violations)
    if violations:
        return {"task_id": task.get("task_id"), "feasible": False, "score": 0.0, "study": study, "violations": violations}
    assert max_fault is not None and min_fault is not None and breaker is not None and pickup is not None
    tol = float(task.get("numeric_tolerance", 1e-3))
    if abs(max_fault - study["max_3ph_fault_ka"]) > tol:
        violations.append("max_3ph_fault_ka does not match recomputed study")
    if abs(min_fault - study["min_2ph_fault_ka"]) > tol:
        violations.append("min_2ph_fault_ka does not match recomputed study")
    if breaker + tol < study["minimum_breaker_rating_ka"]:
        violations.append("breaker_interrupting_rating_ka below required safety margin")
    allowed = [float(x) for x in task["short_circuit_case"]["available_breaker_interrupting_ratings_ka"]]
    if not any(abs(breaker - rating) <= tol for rating in allowed):
        violations.append("breaker_interrupting_rating_ka must be one of the available standard ratings")
    if study["selected_breaker_rating_ka"] is not None and breaker - study["selected_breaker_rating_ka"] > tol:
        violations.append("breaker_interrupting_rating_ka is not the smallest feasible standard rating")
    if pickup + tol < study["relay_pickup_min_a"]:
        violations.append("relay_pickup_a_primary below load-margin minimum")
    if pickup - tol > study["relay_pickup_max_a"]:
        violations.append("relay_pickup_a_primary above minimum-fault sensitivity maximum")
    feasible = not violations
    return {
        "task_id": task.get("task_id"),
        "feasible": feasible,
        "score": 1.0 if feasible else 0.0,
        "study": study,
        "submitted": {
            "max_3ph_fault_ka": max_fault,
            "min_2ph_fault_ka": min_fault,
            "breaker_interrupting_rating_ka": breaker,
            "relay_pickup_a_primary": pickup,
        },
        "violations": violations,
    }


def evaluate_files(task_path: Path, submission_path: Path) -> dict[str, Any]:
    return evaluate_case(_load_json(task_path), _load_json(submission_path))
