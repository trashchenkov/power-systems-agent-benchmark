"""Evaluator for wind-power point forecasts from weather inputs and a turbine power curve."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _power_for_speed(case: dict[str, Any], wind_speed: float, density: float) -> float:
    turbine = case["turbine"]
    curve = case["power_curve"]
    ref_density = float(case.get("reference_air_density_kg_m3", 1.225))
    corrected_speed = float(wind_speed) * (float(density) / ref_density) ** (1.0 / 3.0)
    cut_in = float(curve["cut_in_m_s"])
    rated_speed = float(curve["rated_m_s"])
    cut_out = float(curve["cut_out_m_s"])
    rated_total_mw = float(turbine["count"]) * float(turbine["rated_mw_each"])
    if corrected_speed < cut_in or corrected_speed >= cut_out:
        return 0.0
    if corrected_speed >= rated_speed:
        return rated_total_mw
    frac = ((corrected_speed - cut_in) / (rated_speed - cut_in)) ** 3
    return rated_total_mw * frac


def _history_bias(case: dict[str, Any]) -> float:
    residuals = []
    for row in case["history"]:
        model = _power_for_speed(case, row["wind_speed_m_s"], row["air_density_kg_m3"])
        residuals.append(float(row["actual_power_mw"]) - model)
    return sum(residuals) / len(residuals)


def compute_forecast(task: dict[str, Any]) -> dict[str, Any]:
    case = task["wind_forecast_case"]
    bias = _history_bias(case)
    capacity = float(case["turbine"]["count"]) * float(case["turbine"]["rated_mw_each"])
    forecasts: dict[str, float] = {}
    for row in case["weather_forecast"]:
        raw = _power_for_speed(case, row["wind_speed_m_s"], row["air_density_kg_m3"])
        adjusted = max(0.0, min(capacity, raw + bias))
        forecasts[row["timestamp"]] = round(adjusted, 3)
    step_h = float(case["forecast_step_hours"])
    total_mwh = round(sum(forecasts.values()) * step_h, 3)
    peak_ts = max(forecasts, key=lambda ts: forecasts[ts])
    return {
        "forecast_mw_by_timestamp": forecasts,
        "total_forecast_mwh": total_mwh,
        "peak_timestamp": peak_ts,
        "history_bias_mw": round(bias, 6),
    }


def solve_case(task: dict[str, Any]) -> dict[str, Any]:
    s = compute_forecast(task)
    return {
        "forecast_mw_by_timestamp": s["forecast_mw_by_timestamp"],
        "total_forecast_mwh": s["total_forecast_mwh"],
        "peak_timestamp": s["peak_timestamp"],
        "rationale": "Converted forecast wind speeds to farm output with the published power curve and applied the average historical residual bias."
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
    allowed = {"forecast_mw_by_timestamp", "total_forecast_mwh", "peak_timestamp", "rationale"}
    extra = sorted(set(submission) - allowed)
    if extra:
        violations.append(f"unknown answer fields: {extra}")
    expected = compute_forecast(task)
    submitted = submission.get("forecast_mw_by_timestamp")
    if not isinstance(submitted, dict):
        violations.append("forecast_mw_by_timestamp must be an object keyed by timestamp")
        submitted = {}
    for ts, exp in expected["forecast_mw_by_timestamp"].items():
        if ts not in submitted:
            violations.append(f"missing forecast timestamp: {ts}")
        else:
            _close(f"forecast_mw_by_timestamp.{ts}", _num(submitted[ts], f"forecast_mw_by_timestamp.{ts}", violations), exp, violations)
    _close("total_forecast_mwh", _num(submission.get("total_forecast_mwh"), "total_forecast_mwh", violations), expected["total_forecast_mwh"], violations)
    if submission.get("peak_timestamp") != expected["peak_timestamp"]:
        violations.append(f"peak_timestamp must be {expected['peak_timestamp']}")
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
