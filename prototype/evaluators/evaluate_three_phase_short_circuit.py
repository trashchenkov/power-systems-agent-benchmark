"""Evaluator for IEC 60909-style three-phase short-circuit currents.

Computes the canonical max/min pair from positive-sequence per-unit impedances:

- maximum initial symmetrical current Ik_max: equivalent voltage source with
  voltage factor c_max and a bolted (metallic) fault — fault resistance is
  neglected, per IEC 60909 practice for equipment-rating currents;
- minimum current Ik_min: voltage factor c_min with the published fault/contact
  resistance included — the protection-sensitivity current.
"""

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
    c_max = float(case["voltage_factor_cmax"])
    c_min = float(case["voltage_factor_cmin"])
    base_current_ka = base_mva / (SQRT3 * voltage_kv)
    components = case["positive_sequence_impedances_pu"]
    z_network = sum((_zpu(component) for component in components), complex(0.0, 0.0))
    if abs(z_network) <= 0:
        raise ValueError("network impedance must be non-zero")
    rf = float(case.get("fault_resistance_pu", 0.0))
    z_min_path = z_network + complex(rf, 0.0)
    ik_max_ka = c_max / abs(z_network) * base_current_ka
    sk_max_mva = SQRT3 * voltage_kv * ik_max_ka
    ik_min_ka = c_min / abs(z_min_path) * base_current_ka
    return {
        "z_bolted_mag_pu": round(abs(z_network), 6),
        "z_min_mag_pu": round(abs(z_min_path), 6),
        "base_current_ka": round(base_current_ka, 6),
        "ik_max_ka": round(ik_max_ka, 6),
        "sk_max_mva": round(sk_max_mva, 6),
        "ik_min_ka": round(ik_min_ka, 6),
    }


def solve_case(task: dict[str, Any]) -> dict[str, Any]:
    study = compute_three_phase_fault(task)
    return {
        "ik_max_ka": study["ik_max_ka"],
        "sk_max_mva": study["sk_max_mva"],
        "ik_min_ka": study["ik_min_ka"],
        "z_bolted_mag_pu": study["z_bolted_mag_pu"],
        "z_min_mag_pu": study["z_min_mag_pu"],
        "rationale": (
            "Maximum initial symmetrical current from c_max over the bolted positive-sequence "
            "impedance; minimum current from c_min over the impedance including fault resistance."
        ),
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
    allowed = {"ik_max_ka", "sk_max_mva", "ik_min_ka", "z_bolted_mag_pu", "z_min_mag_pu", "rationale"}
    extra = sorted(set(submission) - allowed)
    if extra:
        violations.append(f"unknown answer fields: {extra}")
    expected = compute_three_phase_fault(task)
    tol = task.get("tolerances", {})
    abs_tol = float(tol.get("absolute", 1e-3))
    rel_tol = float(tol.get("relative", 1e-3))
    for key in ("ik_max_ka", "sk_max_mva", "ik_min_ka", "z_bolted_mag_pu", "z_min_mag_pu"):
        _close(key, _num(submission, key, violations), expected[key], abs_tol, rel_tol, violations)
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
