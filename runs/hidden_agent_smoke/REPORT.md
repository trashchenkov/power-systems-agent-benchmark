# Hidden agent runs — full 41-family generated set (2026-06-11, case_301)

Three CLI agents ran the complete hidden set: one generated `case_301` per
family from `scripts/generate_hidden_cases.py` with a random private seed
(48 hex chars, not recorded anywhere). Packets were prepared with the standard
hidden redaction and are deliberately NOT committed; only run results are.
Same agents, models, prompts, and 600 s per-case timeout as the public matrix.

## Run artifacts

- Codex CLI 0.139.0, `gpt-5.5` medium: `runs/hidden_agent_smoke/codex-hidden301/`
- OpenCode 1.15.13, `deepseek-v4-flash`: `runs/hidden_agent_smoke/opencode-hidden301/`
- Cursor agent CLI, `composer-2.5`: `runs/hidden_agent_smoke/cursor-hidden301/`

## Public vs hidden

| agent (model) | public feasible | hidden feasible | public mean | hidden mean |
|---|---|---|---|---|
| codex (gpt-5.5 medium) | 39/41 | **38/41** | 0.947 | **0.919** |
| cursor (composer-2.5) | **41/41** | 35/41 | **0.995** | 0.846 |
| opencode (deepseek-v4-flash) | 37/41 | 35/41 | 0.900 | 0.846 |

Headline: **the ranking flips on hidden cases.** Cursor led the public core
(41/41) but degrades most on unseen draws (-6 feasible); codex degrades least
(-1) and takes the hidden lead. A public-only leaderboard would have crowned
the wrong agent — this is the concrete argument for hidden evaluation.

## Hidden failure notes

- Genuine capability failures dominate: volt-var control under deeper hidden
  excursions (codex and opencode violated limits; cursor burned the full 600 s
  timeout on it — rc 124, the only no-submission case in 123 runs),
  EV/V2G dispatch step and sign handling (opencode, cursor),
  MAS lead-agent selection (opencode), N-1 commitment choice and meter-coverage
  optimization (cursor), rolling-dispatch SOC self-consistency (cursor).
- `transient_stability_prediction` failed codex and opencode again with
  different numbers while cursor passed — the risk-score specification is
  flagged for an explicit-formula review.
- `islanded_microgrid_pq_dispatch` failed all three agents with similar
  voltage mismatches (two agents identically): suspected next spec-ambiguity
  candidate — likely alternative Q-dispatch optima; should get the same
  re-simulate-and-cost-gap treatment as the other microgrid families.
- Identical partial credits across all three agents (`contingency_screening`
  0.8, `flisr_restoration` 0.96, `pf_voltage_repair` 0.9348) suggest the
  reference solutions in those evaluators have tie-break conventions worth a
  review pass; low priority.

## Integrity finding: one agent reached the oracle

Cursor's pass on hidden `transient_stability_prediction` is contaminated: its
own run log states the submission "evaluates as feasible with a score of 1.0",
i.e. the agent located and executed the evaluator and self-checked against the
oracle. This was possible because packets lived inside the repository working
tree and the harness ran agents with the repository as the working directory —
the prohibition existed only in the packet instructions. Codex and OpenCode,
judging by their failures on the same family, did not exploit this. Treat
cursor's hidden feasible count as <= 35/41 (34/41 excluding the contaminated
case); the ranking-flip conclusion is unaffected (it strengthens). The harness
has since been fixed: each case now runs in a sandbox copy of the packet
outside the repository, with the sandbox as cwd and without BENCH_ROOT or repo
PYTHONPATH. Cursor's earlier public passes of the same family cannot be
audited from its summary-only logs and should be treated with the same
suspicion.

## Revision run (sandboxed harness, fixed families)

After the harness isolation fix and the two family fixes, fresh hidden draws
(case_302 for the fixed families; the original case_301 for pv_volt_var) were
re-run for codex and opencode under the sandboxed runner (cursor re-run
deferred — its CLI is slow and the operator session ended):

- `islanded_microgrid_pq_dispatch` (re-simulate + cost gap): codex 1.0,
  opencode 1.0 — confirms the all-three-agents failure was a spec defect.
- `transient_stability_prediction` (risk formula pinned): codex 1.0,
  opencode 1.0. Codex's first attempt exposed a tolerance-boundary defect —
  a numerically correct answer differing only in the rounding convention at
  the .0005 half-step was rejected by the 1e-3 tolerance; the evaluator
  tolerance now absorbs rounding-convention differences (2.5e-3).
- `pv_volt_var` hidden: codex and opencode fail on voltage limits again —
  a stable, genuine capability failure.

Artifacts: runs/hidden_agent_smoke/{codex,opencode}-hidden-revision1/
(opencode evaluated from its written submissions; its chain was stopped
before summary generation).

## Protocol note

This run burned its seed (the operator machine ran all three agents), so
case_301 should be treated as a development snapshot. For a citable
leaderboard round, regenerate with a fresh seed on an isolated evaluation
host, run agents, and publish only aggregate results.

---

# Historical: case_101 normalized run (pre domain fixes)


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
