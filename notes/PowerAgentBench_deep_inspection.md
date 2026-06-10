# PowerAgentBench deep inspection

Date: 2026-06-08T05:53:09.799463+00:00
Local clone: `/root/tmp/PowerAgentBench`
Commit: `e6bfc96`
Remote: https://github.com/Power-Agent/PowerAgentBench

## What it is

PowerAgentBench is a small but directly relevant benchmark repository for AI agents on power-system operational/planning tasks. The current public release focuses on steady-state studies around IEEE 39-bus.

## Structure

```text
cases/case39/pypsa/case39.nc
cases/case39/matpower/case39.m
cases/case39/pandapower/case39.json
benchmarks/steady/level_1/
benchmarks/steady/level_2/
poweragentbench/benchmark_utils.py
poweragentbench/steady_state_agentic.py
poweragentbench/llm_agent_adapter.py
scripts/*.py
```

## Level 1 pattern

Task: AC steady-state N-1 audit and mitigation.

Agent/competitor receives:

- public case;
- curated contingency set: L7, L12, L20 outages;
- discrete bounded action space;
- action costs;
- solution JSON contract.

Evaluator:

- applies submitted actions;
- runs base-case AC PF;
- runs contingency PF;
- computes line and voltage violation score;
- computes action cost;
- ranks lexicographically: lower remaining violations, then lower action cost.

Reusable ideas:

- curated entry-level task is fine;
- small IEEE case is acceptable for L0/L1;
- discrete bounded action spaces simplify scoring;
- solution JSON can be independent from agent internals.

## Level 2 pattern

Task: agentic N-2 contingency discovery and mitigation.

Public tools:

- `case_summary`
- `rank_base_loading`
- `rank_lodf`
- `validate`
- `redispatch`
- `submit`

Hidden evaluator:

- computes exhaustive N-2 oracle;
- scores search/discovery/evidence/mitigation/tool compliance.

Metrics:

- `reported_top20_recall`
- `validated_top20_recall`
- `found_top20_recall`
- `danger_recall`
- `reported_precision`
- `evidence_rate`
- `best_capture_validated`
- `severity_regret`
- `pre_top20_violation`
- `post_top20_violation`
- `violation_reduction`
- `action_cost`
- `invalid_tool_calls`
- `schema_repairs`
- `type_coercions`
- `duplicate_validation_requests`
- `submitted_explicitly`
- `auto_finalized`
- `validation_budget_used`

## Weaknesses / gaps for our goal

- Scope is narrow: IEEE 39, steady-state.
- Level 2 uses lightweight DC approximation, not full AC security analysis.
- No distribution, dynamics, planning, protection, restoration, DER/microgrid tasks.
- No license declared in GitHub metadata at fetch time, so code reuse needs care.
- Prompt/tool interface is JSON-command style, not necessarily native function calling.
- Current adoption is early-stage.

## Strong patterns to copy

- public/hidden split;
- hidden physical recomputation;
- explicit action/tool schemas;
- budgeted validation;
- evidence rate separate from reported recall;
- invalid/schema/duplicate tool-use diagnostics;
- scripted baselines alongside LLM agent runs;
- multiple case formats for portability.
