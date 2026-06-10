# MVP task contract draft — pandapower-first Power Systems Agent Benchmark

Date: 2026-06-08T05:56:10.940140+00:00

## Benchmark principle

The agent receives natural-language operator instructions plus machine-readable case/tool contracts. The evaluator never trusts the agent's claims; it recomputes all physical quantities from submitted JSON actions and hidden tests.

## Common task package

```text
tasks/<task_family>/<task_id>/
  task.json
  prompt.md
  public_case/
    network.json              # pandapower format for MVP
    metadata.json
  hidden/
    seeds.json                # not released to agents in sealed mode
  schemas/
    final_answer.schema.json
    action.schema.json
  evaluator.py
  reference_solution.json     # optional for development, hidden for leaderboard
```

## Common `task.json`

```json
{
  "task_id": "pf_diag_ieee39_seed001",
  "family": "pf_diagnosis",
  "substrate": "pandapower",
  "case_format": "pandapower_json",
  "public_files": ["public_case/network.json", "prompt.md"],
  "allowed_tools": ["load_case", "run_powerflow", "inspect_violations", "test_action", "submit"],
  "budgets": {"tool_calls": 30, "simulation_calls": 12, "wall_time_s": 300},
  "scoring": {"primary": "remaining_violation_score", "secondary": "action_cost"}
}
```

## Common final answer schema

```json
{
  "diagnosis": "string",
  "actions": [
    {"type": "redispatch", "component_id": "gen_3", "value_mw": 20.0},
    {"type": "load_shed", "component_id": "load_7", "percent": 2.5}
  ],
  "evidence": [
    {"tool_call_id": "...", "claim": "line L17 overloaded in base case"}
  ],
  "confidence": "high|medium|low"
}
```

## MVP family 1 — PF diagnosis and repair

Goal: identify base-case overload/voltage violations and propose bounded corrective actions.

Public tools:

- `case_summary`
- `run_powerflow`
- `inspect_violations`
- `test_actions`
- `submit`

Hidden evaluator:

- loads original case;
- applies submitted actions;
- runs PF;
- scores residual line/voltage violations and action cost.

Metrics:

- PF convergence;
- correct identification of violated elements;
- `remaining_violation_score`;
- `action_cost`;
- invalid action count;
- evidence coverage.

## MVP family 2 — N-1/N-k contingency ranking

Goal: find and rank most severe contingencies under limited validation budget.

Public tools:

- `case_summary`
- `rank_by_base_loading`
- `rank_by_lodf` or `screen_contingencies`
- `validate_contingencies`
- `submit_ranked_contingencies`

Hidden evaluator:

- computes exhaustive oracle on hidden/public variants;
- compares submitted/validated contingencies with oracle top-k.

Metrics:

- recall@k;
- evidence-backed recall@k;
- severity regret;
- validation budget efficiency;
- duplicate validation requests;
- invalid candidate/tool-call rate.

## MVP family 3 — corrective dispatch / OPF repair

Goal: produce an operating point/action plan satisfying constraints at minimal action cost.

Public tools:

- `run_powerflow`
- `run_opf_baseline` maybe available only as a comparator, not oracle;
- `test_dispatch_action`
- `submit_dispatch_plan`

Hidden evaluator:

- validates generator/load/control bounds;
- reruns PF/OPF feasibility check;
- scores objective/action cost and residual violations.

Metrics:

- feasibility;
- objective gap to scripted solver baseline;
- action cost;
- residual violations;
- schema/tool compliance.

## Public/hidden split

Open mode:

- all files visible for development;
- evaluator available.

Sealed mode:

- public cases/tools visible;
- hidden perturbation seeds and oracle results hidden;
- evaluator runs server-side.

Stress mode:

- rerun same agents across randomized but versioned seeds;
- report reliability mean/std and worst-case failures.

## Differentiation from PowerAgentBench

- Use pandapower-first MVP instead of PyPSA/DC Level 2 mechanics.
- Keep simulator-agnostic schema so Grid2Op/OpenDSS/ANDES tiers can be added.
- Include task families beyond contingency search: diagnosis, repair, dispatch.
- Treat LLM-specific behavior as first-class: evidence, invalid calls, schema repairs, duplicate calls, confidence calibration.
