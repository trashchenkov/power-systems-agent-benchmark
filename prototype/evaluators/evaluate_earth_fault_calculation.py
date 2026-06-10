"""Evaluator for single-line-to-ground fault using sequence networks."""

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


def _mag_angle(c: complex) -> dict[str, float]:
    return {"mag_ka": round(abs(c), 6), "angle_deg": round(math.degrees(math.atan2(c.imag, c.real)), 6)}


def compute_earth_fault(task: dict[str, Any]) -> dict[str, Any]:
    case = task["earth_fault_case"]
    base_mva = float(case["base_mva"])
    voltage_kv = float(case["voltage_kv"])
    base_current_ka = base_mva / (SQRT3 * voltage_kv)
    seq = case["sequence_impedances_pu"]
    z1 = _zpu(seq["positive"])
    z2 = _zpu(seq["negative"])
    z0 = _zpu(seq["zero"])
    zf = complex(float(case.get("fault_resistance_pu", 0.0)), 0.0)
    denom = z1 + z2 + z0 + 3.0 * zf
    if abs(denom) <= 0:
        raise ValueError("sequence network denominator must be non-zero")
    # For an SLG fault with prefault phase voltage of 1.0 pu: I1 = I2 = I0 = 1/(Z1+Z2+Z0+3Zf).
    i_seq_pu = 1.0 / denom
    i_fault_pu = 3.0 * i_seq_pu
    i_seq_ka = i_seq_pu * base_current_ka
    i_fault_ka = i_fault_pu * base_current_ka
    return {
        "base_current_ka": round(base_current_ka, 6),
        "denominator_r_pu": round(denom.real, 6),
        "denominator_x_pu": round(denom.imag, 6),
        "i1_ka": _mag_angle(i_seq_ka),
        "i2_ka": _mag_angle(i_seq_ka),
        "i0_ka": _mag_angle(i_seq_ka),
        "fault_current_ka": _mag_angle(i_fault_ka),
        "fault_current_mag_ka": round(abs(i_fault_ka), 6),
        "residual_current_mag_ka": round(abs(i_fault_ka), 6),
    }


def solve_case(task: dict[str, Any]) -> dict[str, Any]:
    study = compute_earth_fault(task)
    return {
        "sequence_currents_ka": {
            "i1": study["i1_ka"],
            "i2": study["i2_ka"],
            "i0": study["i0_ka"],
        },
        "fault_current_ka": study["fault_current_ka"],
        "residual_current_mag_ka": study["residual_current_mag_ka"],
        "rationale": "Computed the single-line-to-ground fault current using I1=I2=I0=1/(Z1+Z2+Z0+3Zf) on the stated per-unit base."
    }


def _num(value: Any, path: str, violations: list[str]) -> float | None:
    try:
        x = float(value)
    except (TypeError, ValueError):
        violations.append(f"{path} must be numeric")
        return None
    if not math.isfinite(x):
        violations.append(f"{path} must be finite")
        return None
    return x


def _get_mag_angle(submission: dict[str, Any], path: str, violations: list[str]) -> dict[str, float | None]:
    cur: Any = submission
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            violations.append(f"missing required field: {path}")
            return {"mag_ka": None, "angle_deg": None}
        cur = cur[part]
    if not isinstance(cur, dict):
        violations.append(f"{path} must be an object with mag_ka and angle_deg")
        return {"mag_ka": None, "angle_deg": None}
    return {
        "mag_ka": _num(cur.get("mag_ka"), f"{path}.mag_ka", violations),
        "angle_deg": _num(cur.get("angle_deg"), f"{path}.angle_deg", violations),
    }


def _close(name: str, actual: float | None, expected: float, abs_tol: float, rel_tol: float, violations: list[str]) -> None:
    if actual is None:
        return
    limit = max(abs_tol, rel_tol * max(1.0, abs(expected)))
    if abs(actual - expected) > limit:
        violations.append(f"{name}={actual:.6g} differs from expected {expected:.6g} by more than {limit:.3g}")


def evaluate_case(task: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    violations: list[str] = []
    allowed = {"sequence_currents_ka", "fault_current_ka", "residual_current_mag_ka", "rationale"}
    extra = sorted(set(submission) - allowed)
    if extra:
        violations.append(f"unknown answer fields: {extra}")
    expected = compute_earth_fault(task)
    tol = task.get("tolerances", {})
    abs_tol = float(tol.get("absolute", 1e-3))
    rel_tol = float(tol.get("relative", 1e-4))
    for seq_name, exp_key in [("i1", "i1_ka"), ("i2", "i2_ka"), ("i0", "i0_ka")]:
        actual = _get_mag_angle(submission, f"sequence_currents_ka.{seq_name}", violations)
        _close(f"sequence_currents_ka.{seq_name}.mag_ka", actual["mag_ka"], expected[exp_key]["mag_ka"], abs_tol, rel_tol, violations)
        _close(f"sequence_currents_ka.{seq_name}.angle_deg", actual["angle_deg"], expected[exp_key]["angle_deg"], 0.01, 1e-4, violations)
    fault = _get_mag_angle(submission, "fault_current_ka", violations)
    _close("fault_current_ka.mag_ka", fault["mag_ka"], expected["fault_current_ka"]["mag_ka"], abs_tol, rel_tol, violations)
    _close("fault_current_ka.angle_deg", fault["angle_deg"], expected["fault_current_ka"]["angle_deg"], 0.01, 1e-4, violations)
    residual = _num(submission.get("residual_current_mag_ka"), "residual_current_mag_ka", violations)
    _close("residual_current_mag_ka", residual, expected["residual_current_mag_ka"], abs_tol, rel_tol, violations)
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
