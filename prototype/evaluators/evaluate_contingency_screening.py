"""Public surrogate evaluator for N-1 contingency screening.

This evaluator is intentionally lightweight: hidden benchmark variants can replace
published post-contingency flows with simulator-computed AC/DC flows while keeping
this submission contract stable.
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


def _components_after_outage(case: dict[str, Any], outaged_branch: str) -> int:
    adjacency: dict[str, set[str]] = {}
    for branch in case.get("branches", []):
        if branch["id"] == outaged_branch:
            continue
        a = branch["from_bus"]
        b = branch["to_bus"]
        adjacency.setdefault(a, set()).add(b)
        adjacency.setdefault(b, set()).add(a)
    buses = set(adjacency)
    for branch in case.get("branches", []):
        buses.add(branch["from_bus"])
        buses.add(branch["to_bus"])
    if not buses:
        return 0
    seen: set[str] = set()
    components = 0
    for bus in sorted(buses):
        if bus in seen:
            continue
        components += 1
        stack = [bus]
        seen.add(bus)
        while stack:
            current = stack.pop()
            for nxt in adjacency.get(current, set()):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
    return components


def _contingency_result(case: dict[str, Any], contingency: dict[str, Any]) -> dict[str, Any]:
    branches = _branch_map(case)
    outaged = contingency["outaged_branch"]
    components = _components_after_outage(case, outaged)
    is_islanding = components > 1
    max_loading = 0.0
    overloaded: list[str] = []
    for branch_id, raw_flow in contingency.get("post_flows_mw", {}).items():
        branch = branches.get(branch_id)
        if branch is None:
            continue
        rating = float(branch["rating_mw"])
        if rating <= 0:
            continue
        loading = abs(float(raw_flow)) / rating * 100.0
        max_loading = max(max_loading, loading)
        if loading > float(case.get("critical_loading_threshold_pct", 100.0)):
            overloaded.append(branch_id)
    return {
        "outaged_branch": outaged,
        "islanding": is_islanding,
        "components": components,
        "max_loading_pct": round(max_loading, 6),
        "overloaded_branches": overloaded,
        "critical": is_islanding or bool(overloaded),
    }


def evaluate_case(case: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    known = {c["id"] for c in case.get("contingencies", [])}
    ranking = submission.get("ranking", [])
    islanding_flags = submission.get("islanding_flags", {})
    violations: list[str] = []

    if not isinstance(ranking, list):
        violations.append("ranking must be a list")
        ranking = []
    if not isinstance(islanding_flags, dict):
        violations.append("islanding_flags must be an object")
        islanding_flags = {}

    unknown_ranked = [cid for cid in ranking if cid not in known]
    for cid in unknown_ranked:
        violations.append(f"unknown contingency in ranking: {cid}")

    contingency_results = {
        contingency["id"]: _contingency_result(case, contingency)
        for contingency in case.get("contingencies", [])
    }
    critical = [cid for cid, result in contingency_results.items() if result["critical"]]
    islanding = [cid for cid, result in contingency_results.items() if result["islanding"]]

    ranked_set = set(ranking)
    missed_critical = [cid for cid in critical if cid not in ranked_set]
    missed_islanding = [cid for cid in islanding if islanding_flags.get(cid) is not True]
    false_islanding = [cid for cid, flag in islanding_flags.items() if flag is True and cid in known and cid not in islanding]

    for cid in missed_critical:
        violations.append(f"missed critical contingency: {cid}")
    for cid in missed_islanding:
        violations.append(f"missed islanding flag: {cid}")
    for cid in false_islanding:
        violations.append(f"false islanding flag: {cid}")

    feasible = not violations
    if feasible:
        ideal_order = sorted(critical, key=lambda cid: contingency_results[cid]["max_loading_pct"], reverse=True)
        ranked_critical = [cid for cid in ranking if cid in critical]
        order_penalty = sum(
            1 for expected, actual in zip(ideal_order, ranked_critical) if expected != actual
        )
        extra_penalty = max(0, len(ranking) - len(known)) * 5
        score = max(0.0, 1.0 - (5.0 * order_penalty + extra_penalty) / 100.0)
    else:
        score = 0.0

    return {
        "task_id": case.get("task_id"),
        "feasible": feasible,
        "score": round(score, 6),
        "critical_contingencies": critical,
        "missed_critical_contingencies": missed_critical,
        "islanding_contingencies": islanding,
        "missed_islanding": missed_islanding,
        "false_islanding": false_islanding,
        "contingency_results": contingency_results,
        "violations": violations,
    }


def evaluate_files(case_path: str | Path, submission_path: str | Path) -> dict[str, Any]:
    return evaluate_case(_load_json(case_path), _load_json(submission_path))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate an N-1 contingency screening submission.")
    parser.add_argument("case", help="Path to public/hidden case JSON")
    parser.add_argument("submission", help="Path to submission JSON")
    args = parser.parse_args()
    print(json.dumps(evaluate_files(args.case, args.submission), ensure_ascii=False, indent=2))
