"""Evaluator for bad-data identification in a DC WLS state estimator.

The case publishes raw measurements containing a non-stealthy false-data
injection. The evaluator rebuilds the DC measurement model, recomputes the
weighted least-squares estimate, runs the iterative largest-normalized-residual
test (Abur & Exposito style), and compares the submitted attacked-measurement
set and corrected state against that recomputation.

Scope note: coordinated stealthy FDI attacks are intentionally out of scope for
this surrogate. They are constructed to leave residuals unchanged and cannot be
found by residual tests; this case models a naive (detectable) injection.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

ALLOWED = {"attacked_measurements", "corrected_state", "rationale"}


def _load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def _spec(case: dict[str, Any]) -> dict[str, Any]:
    inputs = case.get("public_inputs", {})
    return inputs if "network" in inputs else case


def _non_slack_buses(spec: dict[str, Any]) -> list[str]:
    slack = spec["network"]["slack_bus"]
    buses: list[str] = []
    for branch in spec["network"]["branches"]:
        for bus in (branch["from_bus"], branch["to_bus"]):
            if bus != slack and bus not in buses:
                buses.append(bus)
    return buses


def _state_names(spec: dict[str, Any]) -> list[str]:
    return [f"theta_{bus.lstrip('b')}" for bus in _non_slack_buses(spec)]


def _h_row(spec: dict[str, Any], measurement: dict[str, Any]) -> list[float]:
    buses = _non_slack_buses(spec)
    index = {bus: i for i, bus in enumerate(buses)}
    branches = {branch["id"]: branch for branch in spec["network"]["branches"]}
    row = [0.0] * len(buses)

    def add(bus: str, value: float) -> None:
        if bus in index:
            row[index[bus]] += value

    if measurement["type"] == "flow":
        branch = branches[measurement["branch_id"]]
        susceptance = 1.0 / float(branch["x_pu"])
        add(branch["from_bus"], susceptance)
        add(branch["to_bus"], -susceptance)
    elif measurement["type"] == "injection":
        bus = measurement["bus_id"]
        for branch in branches.values():
            susceptance = 1.0 / float(branch["x_pu"])
            if branch["from_bus"] == bus:
                add(bus, susceptance)
                add(branch["to_bus"], -susceptance)
            elif branch["to_bus"] == bus:
                add(bus, susceptance)
                add(branch["from_bus"], -susceptance)
    else:
        raise ValueError(f"unknown measurement type: {measurement['type']}")
    return row


def _solve(matrix: list[list[float]], rhs: list[float]) -> list[float]:
    n = len(rhs)
    a = [list(matrix[i]) + [rhs[i]] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) < 1e-12:
            raise ValueError("singular gain matrix")
        a[col], a[pivot] = a[pivot], a[col]
        for r in range(n):
            if r != col:
                factor = a[r][col] / a[col][col]
                for c in range(col, n + 1):
                    a[r][c] -= factor * a[col][c]
    return [a[i][n] / a[i][i] for i in range(n)]


def _inverse(matrix: list[list[float]]) -> list[list[float]]:
    n = len(matrix)
    columns = [_solve(matrix, [1.0 if i == col else 0.0 for i in range(n)]) for col in range(n)]
    return [[columns[j][i] for j in range(n)] for i in range(n)]


def _wls(spec: dict[str, Any], measurements: list[dict[str, Any]]) -> tuple[list[float], list[list[float]]]:
    n = len(_non_slack_buses(spec))
    gain = [[0.0] * n for _ in range(n)]
    rhs = [0.0] * n
    for measurement in measurements:
        row = _h_row(spec, measurement)
        weight = 1.0 / float(measurement["sigma_pu"]) ** 2
        z = float(measurement["value_pu"])
        for i in range(n):
            rhs[i] += weight * row[i] * z
            for j in range(n):
                gain[i][j] += weight * row[i] * row[j]
    return _solve(gain, rhs), _inverse(gain)


def _normalized_residuals(
    spec: dict[str, Any],
    measurements: list[dict[str, Any]],
    state: list[float],
    gain_inverse: list[list[float]],
) -> list[tuple[float, str]]:
    n = len(state)
    result = []
    for measurement in measurements:
        row = _h_row(spec, measurement)
        sigma = float(measurement["sigma_pu"])
        predicted = sum(row[i] * state[i] for i in range(n))
        residual = float(measurement["value_pu"]) - predicted
        sensitivity = sum(row[i] * gain_inverse[i][j] * row[j] for i in range(n) for j in range(n))
        omega = sigma * sigma - sensitivity
        normalized = abs(residual) / math.sqrt(omega) if omega > 1e-12 else 0.0
        result.append((normalized, measurement["id"]))
    return result


def _expected(case: dict[str, Any]) -> dict[str, Any]:
    spec = _spec(case)
    threshold = float(spec["residual_threshold"])
    active = list(spec["measurements"])
    flagged: list[str] = []
    n_states = len(_non_slack_buses(spec))
    while True:
        if len(active) <= n_states:
            raise ValueError("insufficient measurement redundancy after removals")
        state, gain_inverse = _wls(spec, active)
        residuals = _normalized_residuals(spec, active, state, gain_inverse)
        largest, largest_id = max(residuals)
        if largest <= threshold:
            break
        flagged.append(largest_id)
        active = [m for m in active if m["id"] != largest_id]
    return {
        "attacked_measurements": sorted(flagged),
        "corrected_state": {name: round(state[i], 6) for i, name in enumerate(_state_names(spec))},
    }


def evaluate_case(case: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    spec = _spec(case)
    expected = _expected(case)
    tolerance = float(spec.get("state_error_tolerance_rad", 0.002))
    known = {m["id"] for m in spec["measurements"]}
    violations: list[str] = []

    extra = set(submission) - ALLOWED
    if extra:
        violations.append(f"unknown answer fields: {sorted(extra)}")

    attacked = submission.get("attacked_measurements", [])
    if not isinstance(attacked, list):
        violations.append("attacked_measurements must be a list")
        attacked = []
    predicted = {str(mid) for mid in attacked}
    for mid in sorted(predicted - known):
        violations.append(f"unknown measurement id: {mid}")
    expected_set = set(expected["attacked_measurements"])
    for mid in sorted(expected_set - predicted):
        violations.append(f"missed bad-data measurement: {mid}")
    for mid in sorted((predicted & known) - expected_set):
        violations.append(f"false bad-data alarm: {mid}")

    corrected = submission.get("corrected_state", {})
    if not isinstance(corrected, dict):
        violations.append("corrected_state must be an object")
        corrected = {}
    max_state_error = 0.0
    state_errors: dict[str, float] = {}
    for name, expected_value in expected["corrected_state"].items():
        if name not in corrected:
            violations.append(f"corrected_state missing {name}")
            continue
        try:
            error = abs(float(corrected[name]) - float(expected_value))
        except (TypeError, ValueError):
            violations.append(f"corrected_state.{name} must be numeric")
            continue
        state_errors[name] = round(error, 6)
        max_state_error = max(max_state_error, error)
        if error > tolerance:
            violations.append(
                f"corrected_state.{name} deviates from recomputed WLS estimate by {error:.6f} > {tolerance:.6f}"
            )

    feasible = not violations
    return {
        "task_id": case.get("task_id"),
        "feasible": feasible,
        "score": 1.0 if feasible else 0.0,
        "expected_attacked_measurements": expected["attacked_measurements"],
        "expected_corrected_state": expected["corrected_state"],
        "max_state_error_rad": round(max_state_error, 6),
        "state_errors": state_errors,
        "violations": violations,
    }


def evaluate_files(case_path: str | Path, submission_path: str | Path) -> dict[str, Any]:
    return evaluate_case(_load_json(case_path), _load_json(submission_path))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate a DC-WLS bad-data identification submission.")
    parser.add_argument("case", help="Path to public/hidden case JSON")
    parser.add_argument("submission", help="Path to submission JSON")
    args = parser.parse_args()
    print(json.dumps(evaluate_files(args.case, args.submission), ensure_ascii=False, indent=2))
