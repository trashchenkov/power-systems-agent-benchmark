"""Greedy public baseline for the voltage-repair prototype family."""

from __future__ import annotations

from typing import Any


def solve_case(case: dict[str, Any]) -> dict[str, Any]:
    """Return a simple bounded action plan that repairs voltage violations.

    The public surrogate uses linear voltage sensitivities:
    final_v = base_v + sensitivity * action_value.
    This baseline greedily picks the cheapest positive-sensitivity action for each
    undervoltage bus and the cheapest negative-sensitivity action for each
    overvoltage bus.
    """
    limits = case["limits"]
    min_vm = float(limits["min_vm_pu"])
    max_vm = float(limits["max_vm_pu"])
    base_voltage = {bus: float(value) for bus, value in case["base_voltage_pu"].items()}
    sensitivities = case.get("sensitivities", {})
    action_bounds = case.get("action_bounds", {})

    actions: dict[str, dict[str, float]] = {}
    for bus, vm_pu in base_voltage.items():
        if min_vm <= vm_pu <= max_vm:
            continue

        target_delta = min_vm - vm_pu if vm_pu < min_vm else max_vm - vm_pu
        candidates: list[tuple[float, str, float]] = []
        for action_name, sensitivity_raw in sensitivities.get(bus, {}).items():
            sensitivity = float(sensitivity_raw)
            if sensitivity == 0.0 or target_delta / sensitivity < 0.0:
                continue
            bounds = action_bounds.get(action_name)
            if bounds is None:
                continue
            required = target_delta / sensitivity
            bounded = max(float(bounds["min"]), min(float(bounds["max"]), required))
            cost = abs(bounded) * float(bounds.get("cost_per_unit", 0.0))
            candidates.append((cost, action_name, bounded))

        if candidates:
            _, action_name, value = min(candidates, key=lambda item: item[0])
            actions.setdefault(bus, {})[action_name] = round(value, 6)

    return {
        "actions": actions,
        "rationale": "Greedy linear-sensitivity repair baseline using the cheapest bounded action per violated bus.",
    }
