"""Evaluator for three-phase short-circuit current from per-unit impedances."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

SQRT3 = math.sqrt(3.0)


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _zpu(value: dict[str, Any]) -> complex:
    return complex(float(value.get("r_pu", 0.0)), float(value.get("x_pu", 0.0)))


def compute_three_phase_fault(task: dict[str, Any]) -> dict[str, Any]:
    case = task["short_circuit_case"]
    base_mva = float(case["base_mva"])
    voltage_kv = float(case["voltage_kv"])
    base_current_ka = base_mva / (SQRT3 * voltage_kv)
    components = case["positive_sequence_impedances_pu"]
    z_total = sum((_zpu(component) for component in components), complex(0.0, 0.0))
    rf = float(case.get("fault_resistance_pu", 0.0))
    z_fault = z_total + complex(rf, 0.0)
    if abs(z_fault) <= 0:
        raise ValueError("total fault impedance must be non-zero")
    i_pu = 1.0 / abs(z_fault)
    fault_current_ka = i_pu * base_current_ka
    fault_mva = SQRT3 * voltage_kv * fault_current_ka
    return {
        "z_total_r_pu": round(z_fault.real, 6),
        "z_total_x_pu": round(z_fault.imag, 6),
        "z_total_mag_pu": round(abs(z_fault), 6),
        "base_current_ka": round(base_current_ka, 6),
        "fault_current_ka": round(fault_current_ka, 6),
        "fault_mva": round(fault_mva, 6),
    }


def solve_case(task: dict[str, Any]) -> dict[str, Any]:
    study = compute_three_phase_fault(task)
    return {
        "fault_current_ka": study["fault_current_ka"],
        "fault_mva": study["fault_mva"],
        "z_total_mag_pu": study["z_total_mag_pu"],
        "rationale": "Computed the bolted three-phase fault current from the sum of positive-sequence source, transformer, and line impedances on the given per-unit base."
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


def _close(name: str, actual: float | None, expected: float, abs_tol: float, rel_tol: float, violations: list[str]) -> None:
    if actual is None:
        return
    limit = max(abs_tol, rel_tol * max(1.0, abs(expected)))
    if abs(actual - expected) > limit:
        violations.append(f"{name}={actual:.6g} differs from expected {expected:.6g} by more than {limit:.3g}")


def evaluate_case(task: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    violations: list[str] = []
    allowed = {"fault_current_ka", "fault_mva", "z_total_mag_pu", "rationale"}
    extra = sorted(set(submission) - allowed)
    if extra:
        violations.append(f"unknown answer fields: {extra}")
    expected = compute_three_phase_fault(task)
    tol = task.get("tolerances", {})
    abs_tol = float(tol.get("absolute", 1e-3))
    rel_tol = float(tol.get("relative", 1e-4))
    fault_current = _num(submission, "fault_current_ka", violations)
    fault_mva = _num(submission, "fault_mva", violations)
    zmag = _num(submission, "z_total_mag_pu", violations)
    _close("fault_current_ka", fault_current, expected["fault_current_ka"], abs_tol, rel_tol, violations)
    _close("fault_mva", fault_mva, expected["fault_mva"], abs_tol, rel_tol, violations)
    _close("z_total_mag_pu", zmag, expected["z_total_mag_pu"], abs_tol, rel_tol, violations)
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
