# Public agent runs — full 41-task core (2026-06-11)

Three CLI agents ran the complete 41-task public core after the domain-content
fixes (RoCoF, FDI/WLS redesign, equal-area CCT, IEC 60909 max/min pair) and the
family swap (transformer / cable / harmonics in; boilers / Sobol out).

## Run artifacts

- Codex CLI 0.139.0, model `gpt-5.5` (reasoning effort medium):
  `runs/public_agent_smoke/codex-20260611T074107Z-public41-stable/`
- OpenCode 1.15.13, model `deepseek-v4-flash`:
  `runs/public_agent_smoke/opencode-20260611T074107Z-public41-stable/`
- Cursor agent CLI, models `composer-2.5` / `composer-2.5-fast`:
  `runs/public_agent_smoke/cursor-20260611T083324Z-public41-stable/`

## Aggregate results

| agent (model) | feasible | perfect (score = 1.0) | mean_score |
|---|---|---|---|
| cursor (composer-2.5 / -fast) | 33/41 | 29/41 | 0.800 |
| codex (gpt-5.5 medium) | 32/41 | 28/41 | 0.776 |
| opencode (deepseek-v4-flash) | 31/41 | 29/41 | 0.754 |

Metric semantics: `feasible` means every hard constraint was satisfied — the
solution is admissible but may still carry quality penalties (ranking order,
action cost, switching count), so it is not the count of perfectly solved
tasks; `perfect` counts score = 1.0 exactly. Note the metrics disagree on the
ordering: cursor leads on feasible and mean_score, while opencode ties cursor
on perfect solves and codex drops to third — quality penalties and infeasible
counts trade off differently per agent.

Headline: the public core now discriminates. No agent saturates, the three
surfaces separate, and every failure is a domain failure — all 123 case runs
produced a submission (zero harness/auth/no-submission failures).

## Failure taxonomy

12 of 41 families failed for at least one agent. Reading the violations splits
them into two very different groups.

### A. Genuine capability differences (agents disagree)

- `pv_volt_var` — opencode violated voltage limits; codex/cursor cleared them
  (same discriminator as the earlier hidden-case runs).
- `ibr_short_circuit_frt` — opencode got the FRT verdict wrong; others passed.
- `ev_v2g_outage_schedule` — codex inverted the stated discharge sign
  convention; others passed.
- `transient_stability_prediction` — cursor passed; codex and opencode
  miscomputed risk scores in different ways.
- `microgrid_economic_dispatch` — codex alone passed.
- Partial credit separated agents too: `contingency_screening` ranking order
  (0.9 for codex/cursor), `pf_voltage_repair` action cost (0.958 all),
  `flisr_restoration` switching count (0.96 all).

### B. Suspected spec ambiguities (all three agents fail identically)

These look like task-definition problems, not agent problems, and should be
fixed before treating the affected families as discriminating:

1. `min_synchronous_share` — submission_schema text says "online synchronous MW
   divided by demand MW", which literally describes a fraction; codex and
   cursor dutifully returned 0.51 while the evaluator expects 51.0 (the field
   name says `_pct`). Fix the schema wording to "in percent (0-100)".
2. `wind_prediction_interval` — the evaluator computes quantiles by linear
   interpolation over order statistics (pos = q*(n-1)), but the instructions
   never state the convention; all three agents used a different one and missed
   p10 by the same margin. State the convention in the instructions.
3. `wind_power_forecast` — same family of problem: the bias-correction
   convention is underspecified; all three agents converged on answers that
   differ from the evaluator by similar amounts.
4. `hydro_thermal_storage_uc` — all three agents reported `gas: 0.0` for hours
   where the unit is decommitted; the evaluator requires the key set to equal
   the committed units exactly and rejects semantically identical zero entries.
   Relax the evaluator to accept zero-valued keys.
5. `fci_saidi_caidi` — all three agents flattened the `baseline.*` /
   `with_fci.*` nesting the same way and got `None` lookups; the submission
   schema needs an explicit nested example.
6. `dynamic_thermal_rating` — codex and opencode converged on the same wrong
   ampacity (778.14 vs expected 810.66; cursor differed differently); the
   heat-balance constants/geometry conventions in the instructions need to be
   made fully explicit against the evaluator.
7. `rolling_microgrid_dispatch` / `microgrid_economic_dispatch` — the evaluator
   demands its exact dispatch vector; submissions that satisfy all constraints
   with different (possibly equal-cost) dispatch are rejected. Score should
   compare the cost gap against the optimum instead of exact dispatch values,
   to tolerate alternative optima.

`min_synchronous_share` sits in both groups: opencode passed it, but the two
failures were unit-convention failures caused by the schema text.

## Interpretation

- Group A is the leaderboard signal: real differences in engineering
  computation and constraint handling.
- Group B currently measures convention-guessing, not engineering; until fixed,
  those families penalize every agent identically and add noise, not signal.
- After fixing group B, a strong agent's ceiling on the public core is roughly
  39-40/41 — expected for an open-book public split; discrimination then lives
  in partial-credit scores and the hidden set.

## Historical note

Earlier 7-task runs (Hermes 7/7, OpenCode 6/7, Codex 0/7 on an expired auth
token) and the hidden case_101 normalized runs predate the domain fixes and the
family swap; they are kept under their original directories but are not
comparable with these results.
