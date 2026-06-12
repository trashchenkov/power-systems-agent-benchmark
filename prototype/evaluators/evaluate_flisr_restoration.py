"""Public surrogate evaluator for FLISR distribution service restoration.

The v0 evaluator uses graph-theoretic checks for fault isolation, radiality,
source reachability, restored priority load, and coarse switch-count cost. Hidden
cases can replace the surrogate with pandapower/OpenDSS power-flow checks while
keeping the same switching-plan submission contract.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def _branch_map(case: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {branch["id"]: branch for branch in case.get("branches", [])}


def _bus_map(case: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {bus["id"]: bus for bus in case.get("buses", [])}


def _closed_branches(case: dict[str, Any], submission: dict[str, Any]) -> tuple[set[str], list[str]]:
    branches = _branch_map(case)
    open_switches = submission.get("open_switches", [])
    close_switches = submission.get("close_switches", [])
    violations: list[str] = []
    if not isinstance(open_switches, list):
        violations.append("open_switches must be a list")
        open_switches = []
    if not isinstance(close_switches, list):
        violations.append("close_switches must be a list")
        close_switches = []
    for switch_id in list(open_switches) + list(close_switches):
        if switch_id not in branches:
            violations.append(f"unknown switch/branch id: {switch_id}")
    closed = {
        branch_id
        for branch_id, branch in branches.items()
        if bool(branch.get("normally_closed", True))
    }
    closed.difference_update(open_switches)
    closed.update(close_switches)
    return closed, violations


def _adjacency(case: dict[str, Any], closed: set[str]) -> dict[str, set[str]]:
    adjacency = {bus["id"]: set() for bus in case.get("buses", [])}
    for branch in case.get("branches", []):
        if branch["id"] not in closed:
            continue
        a = branch["from_bus"]
        b = branch["to_bus"]
        adjacency.setdefault(a, set()).add(b)
        adjacency.setdefault(b, set()).add(a)
    return adjacency


def _reachable(adjacency: dict[str, set[str]], source_bus: str) -> set[str]:
    if source_bus not in adjacency:
        return set()
    seen = {source_bus}
    stack = [source_bus]
    while stack:
        current = stack.pop()
        for nxt in adjacency.get(current, set()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


def _has_cycle(case: dict[str, Any], closed: set[str]) -> bool:
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
        if branch["id"] in closed and not union(branch["from_bus"], branch["to_bus"]):
            return True
    return False


def evaluate_case(case: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    buses = _bus_map(case)
    branches = _branch_map(case)
    source_bus = str(case.get("source_bus", ""))
    faulted = set(case.get("faulted_branches", []))
    closed, violations = _closed_branches(case, submission)

    for branch_id in sorted(faulted):
        if branch_id not in branches:
            violations.append(f"unknown faulted branch: {branch_id}")
        elif branch_id in closed:
            violations.append(f"faulted branch must be open: {branch_id}")

    if _has_cycle(case, closed):
        violations.append("energized network must be radial")

    adjacency = _adjacency(case, closed)
    reachable = _reachable(adjacency, source_bus)
    restored_buses = sorted(
        bus_id
        for bus_id in reachable
        if bus_id != source_bus and float(buses.get(bus_id, {}).get("load_kw", 0.0)) > 0.0
    )
    restored_load_kw = sum(float(buses[bus_id].get("load_kw", 0.0)) for bus_id in restored_buses)
    priority_restored = sum(float(buses[bus_id].get("priority", 1.0)) for bus_id in restored_buses)
    total_priority = sum(float(bus.get("priority", 1.0)) for bus in buses.values() if float(bus.get("load_kw", 0.0)) > 0.0)
    _open = submission.get("open_switches")
    _close_sw = submission.get("close_switches")
    switch_count = len(set(_open if isinstance(_open, list) else [])) + len(
        set(_close_sw if isinstance(_close_sw, list) else [])
    )

    min_priority = float(case.get("min_priority_restored", total_priority))
    if priority_restored < min_priority:
        violations.append(f"priority_restored below minimum {min_priority:.6f}")

    feasible = not violations
    if feasible:
        priority_score = priority_restored / total_priority if total_priority else 1.0
        switch_penalty = float(case.get("switch_penalty", 2.0)) * switch_count
        score = max(0.0, priority_score - switch_penalty / 100.0)
    else:
        score = 0.0

    return {
        "task_id": case.get("task_id"),
        "feasible": feasible,
        "score": round(score, 6),
        "restored_buses": restored_buses,
        "restored_load_kw": round(restored_load_kw, 6),
        "priority_restored": round(priority_restored, 6),
        "switch_count": switch_count,
        "closed_branches": sorted(closed),
        "violations": violations,
    }


def evaluate_files(case_path: str | Path, submission_path: str | Path) -> dict[str, Any]:
    return evaluate_case(_load_json(case_path), _load_json(submission_path))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate a FLISR restoration switching plan.")
    parser.add_argument("case", help="Path to public/hidden case JSON")
    parser.add_argument("submission", help="Path to submission JSON")
    args = parser.parse_args()
    print(json.dumps(evaluate_files(args.case, args.submission), ensure_ascii=False, indent=2))
