"""Evaluator for wind-power prediction intervals from scenario forecasts."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from prototype.evaluators.evaluate_wind_power_forecast import _power_for_speed


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _quantile(values: list[float], q: float) -> float:
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    pos = q * (len(xs) - 1)
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return xs[lo]
    return xs[lo] * (hi - pos) + xs[hi] * (pos - lo)


def compute_intervals(task: dict[str, Any]) -> dict[str, Any]:
    case = task["wind_interval_case"]
    intervals: dict[str, dict[str, float]] = {}
    widths: dict[str, float] = {}
    for horizon in case["horizons"]:
        ts = horizon["timestamp"]
        powers = [
            _power_for_speed(case, s["wind_speed_m_s"], s["air_density_kg_m3"])
            for s in horizon["scenarios"]
        ]
        p10 = round(_quantile(powers, 0.10), 3)
        p50 = round(_quantile(powers, 0.50), 3)
        p90 = round(_quantile(powers, 0.90), 3)
        intervals[ts] = {"p10": p10, "p50": p50, "p90": p90}
        widths[ts] = round(p90 - p10, 3)
    return {
        "prediction_interval_mw_by_timestamp": intervals,
        "interval_width_mw_by_timestamp": widths,
        "average_interval_width_mw": round(sum(widths.values()) / len(widths), 3),
    }


def solve_case(task: dict[str, Any]) -> dict[str, Any]:
    s = compute_intervals(task)
    return {
        "prediction_interval_mw_by_timestamp": s["prediction_interval_mw_by_timestamp"],
        "average_interval_width_mw": s["average_interval_width_mw"],
        "rationale": "Converted every wind scenario through the power curve and reported empirical p10, p50, and p90 intervals for each horizon."
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


def evaluate_case(task: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    violations: list[str] = []
    allowed = {"prediction_interval_mw_by_timestamp", "average_interval_width_mw", "rationale"}
    extra = sorted(set(submission) - allowed)
    if extra:
        violations.append(f"unknown answer fields: {extra}")
    expected = compute_intervals(task)
    submitted = submission.get("prediction_interval_mw_by_timestamp")
    if not isinstance(submitted, dict):
        violations.append("prediction_interval_mw_by_timestamp must be an object keyed by timestamp")
        submitted = {}
    for ts, exp_obj in expected["prediction_interval_mw_by_timestamp"].items():
        obj = submitted.get(ts)
        if not isinstance(obj, dict):
            violations.append(f"missing interval object for timestamp: {ts}")
            continue
        vals = []
        for key, exp in exp_obj.items():
            val = _num(obj.get(key), f"prediction_interval_mw_by_timestamp.{ts}.{key}", violations)
            vals.append(val)
            _close(f"prediction_interval_mw_by_timestamp.{ts}.{key}", val, exp, violations)
        if all(v is not None for v in vals) and not (vals[0] <= vals[1] <= vals[2]):
            violations.append(f"prediction interval for {ts} must satisfy p10 <= p50 <= p90")
    _close("average_interval_width_mw", _num(submission.get("average_interval_width_mw"), "average_interval_width_mw", violations), expected["average_interval_width_mw"], violations)
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
