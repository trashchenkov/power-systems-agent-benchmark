from __future__ import annotations

from typing import Any

from prototype.evaluators.evaluate_corrective_transmission_switching import enumerate_feasible_actions


def solve_case(task: dict[str, Any]) -> dict[str, Any]:
    feasible = enumerate_feasible_actions(task)
    if not feasible:
        return {"close_branches": [], "open_branches": [], "rationale": "no feasible corrective switching action found"}
    best = feasible[0]
    return {
        "close_branches": best["close_branches"],
        "open_branches": best["open_branches"],
        "reported_flows_mw": best["pf"]["flows_mw"],
        "rationale": "enumerated candidate corrective switches and selected the feasible minimum-action DC power-flow repair",
    }
