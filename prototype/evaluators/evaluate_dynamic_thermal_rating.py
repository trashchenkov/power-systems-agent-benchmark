"""Evaluator for a compact dynamic thermal rating case."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

SIGMA = 5.670374419e-8


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _rating_for_step(case: dict[str, Any], weather: dict[str, Any]) -> dict[str, float]:
    conductor = case["conductor"]
    limits = case["thermal_limits"]
    diameter_m = float(conductor["diameter_mm"]) / 1000.0
    area = math.pi * diameter_m
    t_max = float(limits["max_conductor_temperature_c"])
    t_amb = float(weather["ambient_temperature_c"])
    wind = max(float(weather["wind_speed_m_s"]), 0.05)
    solar = float(weather.get("solar_w_per_m2", 0.0))
    absorptivity = float(conductor["solar_absorptivity"])
    emissivity = float(conductor["emissivity"])
    r20 = float(conductor["resistance_ohm_per_km_at_20c"]) / 1000.0
    alpha = float(conductor["resistance_temp_coeff_per_c"])
    r_hot = r20 * (1.0 + alpha * (t_max - 20.0))
    delta_t = max(t_max - t_amb, 0.0)
    # Compact IEEE-738-inspired steady-state balance: I^2 R + solar = convection + radiation.
    conv_w_m = float(case["model_constants"]["convective_w_per_m_c_at_1ms"]) * (wind ** 0.6) * delta_t
    rad_w_m = emissivity * SIGMA * area * ((t_max + 273.15) ** 4 - (t_amb + 273.15) ** 4)
    solar_w_m = absorptivity * solar * diameter_m
    net_cooling = max(conv_w_m + rad_w_m - solar_w_m, 0.0)
    ampacity = math.sqrt(net_cooling / r_hot) if r_hot > 0 else 0.0
    return {
        "timestamp": weather["timestamp"],
        "ambient_temperature_c": t_amb,
        "wind_speed_m_s": wind,
        "net_cooling_w_per_m": round(net_cooling, 6),
        "ampacity_a": round(ampacity, 3),
    }


def compute_ratings(task: dict[str, Any]) -> dict[str, Any]:
    case = task["thermal_rating_case"]
    ratings = [_rating_for_step(case, w) for w in case["weather_series"]]
    min_step = min(ratings, key=lambda x: x["ampacity_a"])
    load = float(case["scheduled_current_a"])
    overload_steps = [r["timestamp"] for r in ratings if load > r["ampacity_a"]]
    return {
        "ratings": ratings,
        "minimum_ampacity_a": round(min_step["ampacity_a"], 3),
        "limiting_timestamp": min_step["timestamp"],
        "scheduled_current_a": load,
        "overload_timestamps": overload_steps,
    }


def solve_case(task: dict[str, Any]) -> dict[str, Any]:
    study = compute_ratings(task)
    return {
        "ampacity_by_timestamp_a": {r["timestamp"]: r["ampacity_a"] for r in study["ratings"]},
        "minimum_ampacity_a": study["minimum_ampacity_a"],
        "limiting_timestamp": study["limiting_timestamp"],
        "overload_timestamps": study["overload_timestamps"],
        "rationale": "Solved steady-state conductor heat balance for every weather point and reported the limiting real-time rating."
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


def _close(name: str, actual: float | None, expected: float, violations: list[str], abs_tol: float = 0.5) -> None:
    if actual is None:
        return
    if abs(actual - expected) > abs_tol:
        violations.append(f"{name}={actual:.6g} differs from expected {expected:.6g} by more than {abs_tol}")


def evaluate_case(task: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    violations: list[str] = []
    allowed = {"ampacity_by_timestamp_a", "minimum_ampacity_a", "limiting_timestamp", "overload_timestamps", "rationale"}
    extra = sorted(set(submission) - allowed)
    if extra:
        violations.append(f"unknown answer fields: {extra}")
    expected = compute_ratings(task)
    submitted_map = submission.get("ampacity_by_timestamp_a")
    if not isinstance(submitted_map, dict):
        violations.append("ampacity_by_timestamp_a must be an object keyed by timestamp")
        submitted_map = {}
    for row in expected["ratings"]:
        ts = row["timestamp"]
        if ts not in submitted_map:
            violations.append(f"missing ampacity for timestamp: {ts}")
            continue
        _close(f"ampacity_by_timestamp_a.{ts}", _num(submitted_map[ts], f"ampacity_by_timestamp_a.{ts}", violations), row["ampacity_a"], violations)
    _close("minimum_ampacity_a", _num(submission.get("minimum_ampacity_a"), "minimum_ampacity_a", violations), expected["minimum_ampacity_a"], violations)
    if submission.get("limiting_timestamp") != expected["limiting_timestamp"]:
        violations.append(f"limiting_timestamp must be {expected['limiting_timestamp']}")
    if sorted(submission.get("overload_timestamps", [])) != sorted(expected["overload_timestamps"]):
        violations.append(f"overload_timestamps must be {expected['overload_timestamps']}")
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
