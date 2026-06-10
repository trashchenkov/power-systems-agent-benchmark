"""Evaluator for distance protection reach and time-delay settings."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _line_impedance_ohm(line: dict[str, Any]) -> complex:
    return complex(float(line["r1_ohm_per_km"]), float(line["x1_ohm_per_km"])) * float(line["length_km"])


def expected_windows(task: dict[str, Any]) -> dict[str, Any]:
    data = task["protection_case"]
    protected = _line_impedance_ohm(data["protected_line"])
    backup_lines = [_line_impedance_ohm(line) for line in data.get("remote_backup_lines", [])]
    shortest_backup = min((abs(z) for z in backup_lines), default=0.0)
    longest_backup = max((abs(z) for z in backup_lines), default=0.0)
    z_line = abs(protected)
    rules = data["setting_rules"]
    load = data["maximum_load"]
    min_load_ohm = float(data["voltage_kv"] ** 2) / float(load["apparent_power_mva"])
    return {
        "z_line_ohm": z_line,
        "shortest_backup_ohm": shortest_backup,
        "longest_backup_ohm": longest_backup,
        "min_load_ohm": min_load_ohm,
        "zone1": {
            "min": rules["zone1_fraction"][0] * z_line,
            "max": rules["zone1_fraction"][1] * z_line,
            "delay_min": 0.0,
            "delay_max": rules["zone1_max_delay_s"],
        },
        "zone2": {
            "min": z_line + rules["zone2_backup_fraction"][0] * shortest_backup,
            "max": z_line + rules["zone2_backup_fraction"][1] * shortest_backup,
            "delay_min": rules["zone2_delay_s"][0],
            "delay_max": rules["zone2_delay_s"][1],
        },
        "zone3": {
            "min": z_line + rules["zone3_backup_fraction"][0] * longest_backup,
            "max": min(
                z_line + rules["zone3_backup_fraction"][1] * longest_backup,
                rules["load_encroachment_fraction"] * min_load_ohm,
            ),
            "delay_min": rules["zone3_delay_s"][0],
            "delay_max": rules["zone3_delay_s"][1],
        },
    }


def solve_nominal_settings(task: dict[str, Any]) -> dict[str, Any]:
    windows = expected_windows(task)
    return {
        "zone1_ohm": round((windows["zone1"]["min"] + windows["zone1"]["max"]) / 2.0, 3),
        "zone2_ohm": round((windows["zone2"]["min"] + windows["zone2"]["max"]) / 2.0, 3),
        "zone3_ohm": round((windows["zone3"]["min"] + windows["zone3"]["max"]) / 2.0, 3),
        "zone1_delay_s": 0.0,
        "zone2_delay_s": round(windows["zone2"]["delay_min"], 3),
        "zone3_delay_s": round(windows["zone3"]["delay_min"], 3),
        "rationale": "Set Zone 1 underreaching the protected line, Zone 2 to cover the line plus part of the shortest remote backup line, and Zone 3 for remote backup while respecting load encroachment and delay coordination."
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
    windows = expected_windows(task)
    violations: list[str] = []
    z1 = _num(submission, "zone1_ohm", violations)
    z2 = _num(submission, "zone2_ohm", violations)
    z3 = _num(submission, "zone3_ohm", violations)
    t1 = _num(submission, "zone1_delay_s", violations)
    t2 = _num(submission, "zone2_delay_s", violations)
    t3 = _num(submission, "zone3_delay_s", violations)
    if violations:
        return {"task_id": task.get("task_id"), "feasible": False, "score": 0.0, "windows": windows, "violations": violations}

    assert z1 is not None and z2 is not None and z3 is not None and t1 is not None and t2 is not None and t3 is not None
    tol = float(task.get("numeric_tolerance", 1e-6))
    for name, value in (("zone1_ohm", z1), ("zone2_ohm", z2), ("zone3_ohm", z3)):
        zone = name.split("_")[0]
        if value < windows[zone]["min"] - tol:
            violations.append(f"{name} below minimum reach")
        if value > windows[zone]["max"] + tol:
            violations.append(f"{name} above maximum reach")
    if not (z1 < z2 < z3):
        violations.append("distance reaches must be strictly increasing: zone1 < zone2 < zone3")
    for name, value in (("zone1_delay_s", t1), ("zone2_delay_s", t2), ("zone3_delay_s", t3)):
        zone = name.split("_")[0]
        if value < windows[zone]["delay_min"] - tol or value > windows[zone]["delay_max"] + tol:
            violations.append(f"{name} outside coordination window")
    if not (t1 <= t2 <= t3):
        violations.append("time delays must be coordinated: zone1 <= zone2 <= zone3")

    feasible = not violations
    return {
        "task_id": task.get("task_id"),
        "feasible": feasible,
        "score": 1.0 if feasible else 0.0,
        "windows": windows,
        "submitted": {
            "zone1_ohm": z1,
            "zone2_ohm": z2,
            "zone3_ohm": z3,
            "zone1_delay_s": t1,
            "zone2_delay_s": t2,
            "zone3_delay_s": t3,
        },
        "violations": violations,
    }


def evaluate_files(task_path: Path, submission_path: Path) -> dict[str, Any]:
    return evaluate_case(_load_json(task_path), _load_json(submission_path))
