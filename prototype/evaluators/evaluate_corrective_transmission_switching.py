"""Evaluator for corrective transmission switching after a contingency.

The task is source-derived from corrective transmission switching for SCUC /
post-contingency operations, but the public artifact is a compact DC-network
instance. The evaluator independently recomputes DC flows after the submitted
switching action; reported flows in the submission are treated as diagnostic
metadata and are not trusted for scoring.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from prototype.evaluators.dc_power_flow import active_branches, dc_power_flow, is_connected


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _as_string_set(value: Any, field: str, violations: list[str]) -> set[str]:
    if value is None:
        return set()
    if not isinstance(value, list):
        violations.append(f"{field}: expected list[str]")
        return set()
    out: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            violations.append(f"{field}: expected list[str]")
            continue
        out.add(item)
    return out


def _branch_by_id(task: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {branch["id"]: branch for branch in task.get("branches", [])}


def _candidate_ids(task: dict[str, Any], action: str) -> set[str]:
    return {
        candidate["branch_id"]
        for candidate in task.get("candidate_switches", [])
        if candidate.get("action") == action
    }


def _evaluate_action(task: dict[str, Any], close_branches: set[str], open_branches: set[str]) -> tuple[dict[str, Any] | None, list[str]]:
    violations: list[str] = []
    branches = active_branches(task, close_branches=close_branches, open_branches=open_branches)
    if not is_connected(task, branches):
        violations.append("switching action islands the network")
        return None, violations
    try:
        pf = dc_power_flow(task, branches)
    except ValueError as exc:
        violations.append(str(exc))
        return None, violations
    overloads = {
        branch_id: round(loading - 100.0, 6)
        for branch_id, loading in pf["loading_pct"].items()
        if loading > 100.0 + float(task.get("flow_tolerance_pct", 1e-6))
    }
    if overloads:
        violations.append(f"post-switching overloads remain: {overloads}")
    return {**pf, "overloads_pct": overloads}, violations


def enumerate_feasible_actions(task: dict[str, Any]) -> list[dict[str, Any]]:
    """Enumerate no-action and one-action candidates for the small public CTS task."""
    candidates = [{"close_branches": [], "open_branches": [], "switch_count": 0}]
    for candidate in task.get("candidate_switches", []):
        action = candidate.get("action")
        branch_id = candidate.get("branch_id")
        if action == "close":
            candidates.append({"close_branches": [branch_id], "open_branches": [], "switch_count": 1})
        elif action == "open":
            candidates.append({"close_branches": [], "open_branches": [branch_id], "switch_count": 1})
    feasible = []
    for candidate in candidates:
        pf, violations = _evaluate_action(task, set(candidate["close_branches"]), set(candidate["open_branches"]))
        max_loading = max(pf["loading_pct"].values()) if pf else float("inf")
        candidate = {**candidate, "pf": pf, "violations": violations, "max_loading_pct": max_loading}
        if pf is not None and not violations:
            feasible.append(candidate)
    feasible.sort(key=lambda item: (item["switch_count"], item["max_loading_pct"], item["close_branches"], item["open_branches"]))
    return feasible


def evaluate_case(task: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    violations: list[str] = []
    if not isinstance(submission, dict):
        return {
            "task_id": task.get("task_id"),
            "feasible": False,
            "score": 0.0,
            "violations": ["submission must be a JSON object"],
        }

    close_branches = _as_string_set(submission.get("close_branches", []), "close_branches", violations)
    open_branches = _as_string_set(submission.get("open_branches", []), "open_branches", violations)
    allowed_close = _candidate_ids(task, "close")
    allowed_open = _candidate_ids(task, "open")
    known = set(_branch_by_id(task))
    unknown = (close_branches | open_branches) - known
    if unknown:
        violations.append(f"unknown branch ids: {sorted(unknown)}")
    disallowed_close = close_branches - allowed_close
    disallowed_open = open_branches - allowed_open
    if disallowed_close:
        violations.append(f"close_branches contains non-candidate branches: {sorted(disallowed_close)}")
    if disallowed_open:
        violations.append(f"open_branches contains non-candidate branches: {sorted(disallowed_open)}")
    overlap = close_branches & open_branches
    if overlap:
        violations.append(f"branches cannot be both opened and closed: {sorted(overlap)}")
    switch_count = len(close_branches) + len(open_branches)
    max_switches = int(task.get("switching_budget", 1))
    if switch_count > max_switches:
        violations.append(f"switching budget exceeded: {switch_count} > {max_switches}")

    pf = None
    action_violations: list[str] = []
    if not violations:
        pf, action_violations = _evaluate_action(task, close_branches, open_branches)
        violations.extend(action_violations)

    feasible_actions = enumerate_feasible_actions(task)
    best_switch_count = feasible_actions[0]["switch_count"] if feasible_actions else None
    best_max_loading = feasible_actions[0]["max_loading_pct"] if feasible_actions else None
    max_loading = max(pf["loading_pct"].values()) if pf else None

    feasible = not violations
    if feasible:
        switch_penalty = 0.02 * max(0, switch_count - (best_switch_count or 0))
        loading_penalty = 0.0 if best_max_loading is None else max(0.0, (max_loading - best_max_loading) / 100.0)
        score = max(0.0, round(1.0 - switch_penalty - loading_penalty, 6))
    else:
        score = 0.0

    return {
        "task_id": task.get("task_id"),
        "feasible": feasible,
        "score": score,
        "close_branches": sorted(close_branches),
        "open_branches": sorted(open_branches),
        "switch_count": switch_count,
        "max_loading_pct": round(max_loading, 6) if max_loading is not None else None,
        "best_known_switch_count": best_switch_count,
        "best_known_max_loading_pct": round(best_max_loading, 6) if best_max_loading is not None else None,
        "flows_mw": pf["flows_mw"] if pf else {},
        "loading_pct": pf["loading_pct"] if pf else {},
        "violations": violations,
    }


def evaluate_files(task_path: Path, submission_path: Path) -> dict[str, Any]:
    return evaluate_case(load_json(task_path), load_json(submission_path))
