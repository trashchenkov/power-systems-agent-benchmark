"""IEEE-1547-style default Volt-VAR curve baseline for PV inverter tasks."""

from __future__ import annotations

from typing import Any


def solve_case(case: dict[str, Any]) -> dict[str, Any]:
    """Return a conservative monotonic Volt-VAR curve.

    Positive q_fraction means reactive injection for low-voltage support;
    negative q_fraction means reactive absorption for high-voltage mitigation.
    """
    return {
        "volt_var_curve": [
            {"voltage_pu": 0.94, "q_fraction": 1.0},
            {"voltage_pu": 0.97, "q_fraction": 0.0},
            {"voltage_pu": 1.03, "q_fraction": 0.0},
            {"voltage_pu": 1.06, "q_fraction": -1.0},
        ],
        "rationale": "Default monotonic Volt-VAR curve: inject Q below nominal band and absorb Q above nominal band.",
    }
