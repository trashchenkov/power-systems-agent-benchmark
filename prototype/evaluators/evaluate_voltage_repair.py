"""Minimal public evaluator for the voltage-repair prototype task.

This is intentionally a dependency-free surrogate contract, not a replacement
for the final pandapower hidden evaluator. It exercises the same benchmark
shape: read a case, apply bounded corrective actions, recompute constraints,
and emit machine-readable scoring evidence.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_case(case: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    limits = case["limits"]
    min_vm = float(limits["min_vm_pu"])
    max_vm = float(limits["max_vm_pu"])
    base_voltage = {bus: float(value) for bus, value in case["base_voltage_pu"].items()}
    sensitivities = case.get("sensitivities", {})
    action_bounds = case.get("action_bounds", {})
    actions = submission.get("actions", {})

    final_voltage = dict(base_voltage)
    violations: list[str] = []
    action_cost = 0.0

    if not isinstance(actions, dict):
        violations.append("actions must be an object keyed by bus id")
        actions = {}
    for bus, bus_actions in actions.items():
        if bus not in final_voltage:
            violations.append(f"unknown bus: {bus}")
            continue
        for action_name, raw_value in bus_actions.items():
            value = float(raw_value)
            bounds = action_bounds.get(action_name)
            if bounds is None:
                violations.append(f"unknown action: {action_name}")
                continue
            if value < float(bounds["min"]) or value > float(bounds["max"]):
                violations.append(f"{bus}.{action_name} out of bounds")
                continue
            sensitivity = float(sensitivities.get(bus, {}).get(action_name, 0.0))
            final_voltage[bus] += sensitivity * value
            action_cost += value * float(bounds.get("cost_per_unit", 0.0))

    for bus, vm_pu in final_voltage.items():
        if vm_pu < min_vm:
            violations.append(f"{bus} undervoltage: {vm_pu:.4f} < {min_vm:.4f}")
        if vm_pu > max_vm:
            violations.append(f"{bus} overvoltage: {vm_pu:.4f} > {max_vm:.4f}")

    feasible = not violations
    score = max(0.0, 1.0 - action_cost / 100.0) if feasible else 0.0

    return {
        "task_id": case.get("task_id"),
        "feasible": feasible,
        "score": round(score, 6),
        "action_cost": round(action_cost, 6),
        "final_voltage_pu": {bus: round(value, 6) for bus, value in final_voltage.items()},
        "violations": violations,
    }


def evaluate_files(case_path: str | Path, submission_path: str | Path) -> dict[str, Any]:
    return evaluate_case(_load_json(case_path), _load_json(submission_path))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate a voltage-repair prototype submission.")
    parser.add_argument("case", help="Path to public/hidden case JSON")
    parser.add_argument("submission", help="Path to submission JSON")
    args = parser.parse_args()
    print(json.dumps(evaluate_files(args.case, args.submission), ensure_ascii=False, indent=2))
