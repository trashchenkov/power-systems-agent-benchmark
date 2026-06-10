"""Evaluator for Ybus construction from branch and shunt network data."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _parse_complex(value: Any) -> complex:
    if isinstance(value, dict):
        return complex(float(value.get("re", 0.0)), float(value.get("im", 0.0)))
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return complex(float(value[0]), float(value[1]))
    if isinstance(value, (int, float)):
        return complex(float(value), 0.0)
    raise ValueError(f"cannot parse complex value: {value!r}")


def _to_entry(value: complex, digits: int = 6) -> dict[str, float]:
    return {"re": round(value.real, digits), "im": round(value.imag, digits)}


def compute_ybus(task: dict[str, Any]) -> dict[str, Any]:
    network = task["network"]
    buses = [str(bus) for bus in network["buses"]]
    idx = {bus: i for i, bus in enumerate(buses)}
    n = len(buses)
    ybus = [[0j for _ in range(n)] for _ in range(n)]

    for branch in network.get("branches", []):
        from_bus = str(branch["from_bus"])
        to_bus = str(branch["to_bus"])
        i = idx[from_bus]
        j = idx[to_bus]
        r = float(branch.get("r_pu", 0.0))
        x = float(branch["x_pu"])
        b = float(branch.get("b_pu", 0.0))
        if math.isclose(r, 0.0, abs_tol=1e-15) and math.isclose(x, 0.0, abs_tol=1e-15):
            raise ValueError(f"zero impedance branch: {branch.get('id')}")
        y = 1 / complex(r, x)
        y_shunt_half = 1j * b / 2.0
        ybus[i][i] += y + y_shunt_half
        ybus[j][j] += y + y_shunt_half
        ybus[i][j] -= y
        ybus[j][i] -= y

    for shunt in network.get("shunts", []):
        bus = str(shunt["bus"])
        ybus[idx[bus]][idx[bus]] += complex(float(shunt.get("g_pu", 0.0)), float(shunt.get("b_pu", 0.0)))

    return {"buses": buses, "ybus": [[_to_entry(value) for value in row] for row in ybus]}


def _shape_violation(submission: dict[str, Any], buses: list[str]) -> str | None:
    if "buses" not in submission or "ybus" not in submission:
        return "submission must contain buses and ybus"
    if [str(bus) for bus in submission["buses"]] != buses:
        return "submission buses must match task bus order"
    matrix = submission["ybus"]
    if not isinstance(matrix, list) or len(matrix) != len(buses):
        return "ybus must be a square matrix with one row per bus"
    for row in matrix:
        if not isinstance(row, list) or len(row) != len(buses):
            return "ybus must be a square matrix with one column per bus"
    return None


def evaluate_case(task: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    expected = compute_ybus(task)
    buses = expected["buses"]
    violations: list[str] = []
    shape_violation = _shape_violation(submission, buses)
    if shape_violation:
        violations.append(shape_violation)
        return {
            "task_id": task.get("task_id"),
            "feasible": False,
            "score": 0.0,
            "violations": violations,
        }

    tolerance = float(task.get("numeric_tolerance", 1e-6))
    max_abs_error = 0.0
    entry_errors: dict[str, float] = {}
    for i, from_bus in enumerate(buses):
        for j, to_bus in enumerate(buses):
            expected_value = _parse_complex(expected["ybus"][i][j])
            try:
                observed_value = _parse_complex(submission["ybus"][i][j])
            except Exception as exc:  # noqa: BLE001 - report invalid entries as benchmark violations.
                violations.append(f"invalid complex entry ybus[{i}][{j}]: {exc}")
                continue
            error = abs(observed_value - expected_value)
            max_abs_error = max(max_abs_error, error)
            if error > tolerance:
                key = f"{from_bus},{to_bus}"
                entry_errors[key] = round(error, 9)

    if entry_errors:
        violations.append("one or more Ybus entries exceed numeric tolerance")
    feasible = not violations
    score = 1.0 if feasible else max(0.0, 1.0 - min(1.0, max_abs_error / max(tolerance * 100.0, 1e-12)))
    return {
        "task_id": task.get("task_id"),
        "feasible": feasible,
        "score": round(score, 6),
        "buses": buses,
        "max_abs_error": round(max_abs_error, 9),
        "entry_errors": entry_errors,
        "expected_ybus": expected["ybus"],
        "violations": violations,
    }


def evaluate_files(task_path: Path, submission_path: Path) -> dict[str, Any]:
    return evaluate_case(_load_json(task_path), _load_json(submission_path))
