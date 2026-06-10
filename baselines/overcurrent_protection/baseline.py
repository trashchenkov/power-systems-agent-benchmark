"""Rule-based public baseline for line overcurrent protection settings."""

from __future__ import annotations

from typing import Any


def solve_case(case: dict[str, Any]) -> dict[str, Any]:
    max_load = float(case["max_load_current_a"])
    min_fault = float(case["min_fault_current_a"])
    load_margin = float(case.get("load_margin_multiplier", 1.2))
    min_sensitivity = float(case.get("min_sensitivity_factor", 1.5))
    downstream_delay = float(case.get("downstream_time_delay_s", 0.0))
    selectivity_margin = float(case.get("selectivity_margin_s", 0.3))

    lower_pickup = max_load * load_margin
    upper_pickup = min_fault / min_sensitivity
    if lower_pickup <= upper_pickup:
        pickup = lower_pickup
    else:
        # No feasible pickup exists; choose the least-bad load-secure pickup so
        # the evaluator exposes the sensitivity violation.
        pickup = lower_pickup

    time_delay = downstream_delay + selectivity_margin
    return {
        "pickup_current_a": round(pickup, 6),
        "time_delay_s": round(time_delay, 6),
        "rationale": "Set pickup at load-margin minimum when sensitivity permits; set delay at downstream delay plus selectivity margin.",
    }
