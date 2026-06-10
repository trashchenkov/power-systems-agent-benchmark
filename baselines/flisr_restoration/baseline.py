"""Greedy critical-load restoration baseline for FLISR tasks."""

from __future__ import annotations

from typing import Any


def _would_cycle(case: dict[str, Any], closed: set[str], candidate: str) -> bool:
    parent: dict[str, str] = {bus["id"]: bus["id"] for bus in case.get("buses", [])}

    def find(x: str) -> str:
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> bool:
        ra = find(a)
        rb = find(b)
        if ra == rb:
            return False
        parent[rb] = ra
        return True

    for branch in case.get("branches", []):
        if branch["id"] in closed or branch["id"] == candidate:
            if not union(branch["from_bus"], branch["to_bus"]):
                return True
    return False


def solve_case(case: dict[str, Any]) -> dict[str, Any]:
    """Open all known faulted branches and close non-cycling tie switches."""
    faulted = set(case.get("faulted_branches", []))
    open_switches = sorted(faulted)
    closed = {
        branch["id"]
        for branch in case.get("branches", [])
        if bool(branch.get("normally_closed", True)) and branch["id"] not in faulted
    }
    close_switches: list[str] = []
    for branch in case.get("branches", []):
        branch_id = branch["id"]
        if bool(branch.get("normally_closed", True)) or branch_id in faulted:
            continue
        if not _would_cycle(case, closed, branch_id):
            closed.add(branch_id)
            close_switches.append(branch_id)
    return {
        "open_switches": open_switches,
        "close_switches": close_switches,
        "rationale": "Open the faulted section and close radial tie switches to restore reachable priority load.",
    }
