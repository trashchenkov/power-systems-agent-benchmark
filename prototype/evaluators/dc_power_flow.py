"""Small dependency-free DC power-flow helpers for executable benchmark evaluators."""

from __future__ import annotations

from collections import deque
from typing import Any


def active_branches(task: dict[str, Any], close_branches: set[str] | None = None, open_branches: set[str] | None = None) -> list[dict[str, Any]]:
    close_branches = close_branches or set()
    open_branches = open_branches or set()
    active = []
    for branch in task.get("branches", []):
        branch_id = branch["id"]
        closed = bool(branch.get("closed", True))
        if branch_id in close_branches:
            closed = True
        if branch_id in open_branches:
            closed = False
        if closed:
            active.append(branch)
    return active


def is_connected(task: dict[str, Any], branches: list[dict[str, Any]]) -> bool:
    buses = [bus["id"] for bus in task.get("buses", [])]
    if not buses:
        return False
    adjacency = {bus: set() for bus in buses}
    for branch in branches:
        adjacency[branch["from_bus"]].add(branch["to_bus"])
        adjacency[branch["to_bus"]].add(branch["from_bus"])
    seen = {buses[0]}
    queue = deque([buses[0]])
    while queue:
        bus = queue.popleft()
        for neighbor in adjacency[bus]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return len(seen) == len(buses)


def _solve_linear_system(matrix: list[list[float]], rhs: list[float]) -> list[float] | None:
    n = len(matrix)
    a = [row[:] for row in matrix]
    b = rhs[:]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(a[row][col]))
        if abs(a[pivot][col]) < 1e-12:
            return None
        a[col], a[pivot] = a[pivot], a[col]
        b[col], b[pivot] = b[pivot], b[col]
        pivot_value = a[col][col]
        for j in range(col, n):
            a[col][j] /= pivot_value
        b[col] /= pivot_value
        for row in range(n):
            if row == col:
                continue
            factor = a[row][col]
            if abs(factor) < 1e-15:
                continue
            for j in range(col, n):
                a[row][j] -= factor * a[col][j]
            b[row] -= factor * b[col]
    return b


def dc_power_flow(task: dict[str, Any], branches: list[dict[str, Any]]) -> dict[str, Any]:
    """Solve a lossless DC power flow and return branch flows in MW.

    Raises ValueError for disconnected/singular networks. The slack angle is fixed
    to zero; injections must sum approximately to zero.
    """
    buses = [bus["id"] for bus in task.get("buses", [])]
    if not buses:
        raise ValueError("task has no buses")
    if not is_connected(task, branches):
        raise ValueError("network is islanded")
    injections = {bus["id"]: float(bus.get("p_mw", 0.0)) for bus in task.get("buses", [])}
    if abs(sum(injections.values())) > 1e-6:
        raise ValueError("bus injections do not balance")

    bus_index = {bus: i for i, bus in enumerate(buses)}
    n = len(buses)
    susceptance = [[0.0 for _ in buses] for _ in buses]
    for branch in branches:
        i = bus_index[branch["from_bus"]]
        j = bus_index[branch["to_bus"]]
        b = 1.0 / float(branch["x_pu"])
        susceptance[i][i] += b
        susceptance[j][j] += b
        susceptance[i][j] -= b
        susceptance[j][i] -= b

    slack = 0
    keep = [i for i in range(n) if i != slack]
    reduced = [[susceptance[i][j] for j in keep] for i in keep]
    rhs = [injections[buses[i]] for i in keep]
    solved = _solve_linear_system(reduced, rhs)
    if solved is None:
        raise ValueError("DC power-flow matrix is singular")

    theta = {buses[slack]: 0.0}
    for value, idx in zip(solved, keep):
        theta[buses[idx]] = value

    flows = {}
    loading_pct = {}
    for branch in branches:
        flow = (theta[branch["from_bus"]] - theta[branch["to_bus"]]) / float(branch["x_pu"])
        flows[branch["id"]] = round(flow, 6)
        loading_pct[branch["id"]] = round(abs(flow) / float(branch["rating_mw"]) * 100.0, 6)
    return {"theta_rad": theta, "flows_mw": flows, "loading_pct": loading_pct}
