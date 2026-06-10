# Hidden agent smoke report — case_101 normalized run

This report compares Hermes CLI/file-toolset and OpenCode on the first harder hidden cases after the benchmark score migration from `0–100` totals to per-case normalized `score ∈ [0,1]` and aggregate `mean_score`.

## Run artifacts

- Hermes: `runs/hidden_agent_smoke/hermes-hidden-101-normalized/`
- OpenCode: `runs/hidden_agent_smoke/opencode-hidden-101-normalized/`
- Hidden task packets: `runs/agent_packets/hidden_101/`

## Aggregate results

- Hermes CLI (`--toolsets file`): `3/3` feasible, `mean_score=0.864412`.
- OpenCode (`opencode/deepseek-v4-flash-free`): `2/3` feasible, `mean_score=0.541778`.

## Per-family results

### `contingency_screening`

- Hermes: feasible, `score=0.8`, no missed critical contingencies, no missed/false islanding flags.
- OpenCode: feasible, `score=0.8`, no missed critical contingencies, no missed/false islanding flags.
- Interpretation: both agents satisfied hard screening requirements, but ranking order was not ideal under the evaluator penalty.

### `pf_voltage_repair`

- Hermes: feasible, `score=0.825333`, `action_cost=17.466667`.
- OpenCode: feasible, `score=0.825333`, `action_cost=17.466667`.
- Interpretation: both agents found a valid repair with the same action cost.

### `pv_volt_var`

- Hermes: feasible, `score=0.967902`, `control_effort_kvar_sum=160.48761`, no voltage violations.
- OpenCode: infeasible, `score=0.0`, `control_effort_kvar_sum=111.541662`.
- OpenCode violations:
  - `voltage outside limits at t_deep_low`
  - `voltage outside limits at t_shallow_high`
  - `voltage outside limits at t_deep_high`
- Interpretation: this hidden case remains the strongest discriminator in the current three-case harder set. OpenCode produced too little/incorrectly shaped reactive control for the hidden voltage extremes, while Hermes cleared the limits.

## Classification

- Hermes failures: none in this hidden normalized run.
- OpenCode failures: task-quality/evaluator failure on `pv_volt_var`; not a CLI/auth failure, because a `submission.json` was produced and evaluated.

## Caveats

- These are still deterministic surrogate hidden cases, not yet full simulator-backed pandapower/OpenDSS hidden evaluators.
- Current hidden set covers only three families: `contingency_screening`, `pf_voltage_repair`, and `pv_volt_var`.
- Historical run directories without the `-normalized` suffix used the old `0–100`/`total_score` convention and should not be directly mixed with this report.
