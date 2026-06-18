# Canonical evaluation round (2026-06)

The single reference round used for the paper, scored by the corrected,
optimum-normalized evaluators.

## Configuration

Three command-line agents, one public case (`case_001`) and one freshly generated
held-out case per family (41 families), 600 s per-case timeout, `--max-attempts 2`
(retry only provider-/transport-transient failures, never quality, contract, or
timeout failures).

| agent | model | CLI version |
|---|---|---|
| codex | gpt-5.5 (medium reasoning) | codex-cli 0.139.0 |
| cursor | composer-2.5 | cursor-agent 2026.06.12-01-15-52-7244546 |
| opencode | deepseek-v4-flash-free | opencode 1.15.13 |

Scoring: deterministic evaluators, each task's score normalized against its reference
optimum so that an optimal solution scores 1.0 (`scripts/evaluate_submission.py`).

## Results (optimum-normalized)

| agent (model) | public feasible | public perfect | public mean | hidden feasible | hidden perfect | hidden mean |
|---|---|---|---|---|---|---|
| codex (gpt-5.5 medium) | 40/41 | 38/41 | 0.973 | 41/41 | 40/41 | 0.995 |
| cursor (composer-2.5) | 40/41 | 39/41 | 0.973 | 41/41 | 41/41 | 1.000 |
| opencode (deepseek-v4-flash-free) | 39/41 | 39/41 | 0.951 | 40/41 | 39/41 | 0.973 |

## Procedure / provenance

- **Public** results were rescored from the recorded public submissions against the
  corrected, normalized evaluators (the agent answers are unchanged; only the
  evaluators were fixed and the score normalized). Raw logs, packets, and
  per-case submissions are not committed; rerun the public split to reproduce them.
- **Held-out** results are from a fresh run on a new private seed (not recorded). Per
  the leak policy only the aggregate summaries are kept in the repo; per-case held-out
  submissions, results, and logs are not published (paper Section 4.4).
- **Cursor held-out `critical_clearing_time`** hit an infrastructure timeout (agent
  hang, no submission written) during the parallel run; it was re-run in isolation
  under the same retry policy and completed feasibly (1.0). No other run triggered a
  retry.

## Corrections applied since the earlier development rounds

1. Four evaluators compared set-valued answers (`committed_units`, `protected_meters`,
   `covered_attack_vectors`, `online_units`, `selected_actions`) as order-sensitive
   lists; fixed to compare them as sets. This turned three previously "failed" public
   cases into correct ones (cursor `protected_meter_placement`; opencode
   `n1_generation_commitment` and `protected_meter_placement`).
2. Scores are now normalized against each task's reference optimum, so
   continuous-objective tasks (`flisr_restoration`, `pf_voltage_repair`, `pv_volt_var`)
   reach 1.0 at the optimum instead of an artificial sub-1.0 cap.
3. The `pv_volt_var` reference solver was rewritten from a fixed IEEE-1547-style curve
   into a true least-effort optimizer (the previous baseline was beatable).
4. (Earlier) the `fault_section_localization` evaluator had an off-by-one in the
   fault-current-indicator model, found because independent agents agreed against the
   evaluator; fixed.

## Findings

1. **Near-saturation.** codex and cursor score close to the maximum and are nearly
   indistinguishable; opencode trails modestly. The benchmark separates the spectrum
   (open vs frontier) and surfaces shared blind spots, but does not sharply rank the
   leading agents on this compact tier.
2. **Public and held-out agree.** Every agent scores at least as high on the freshly
   generated held-out cases as on the public ones, so the contamination signature
   (public above held-out) is absent.
3. **Genuine remaining gaps.** opencode fails `rolling_microgrid_dispatch` (hidden) and
   `pv_volt_var` (public); `contingency_screening` is partial for codex (0.8 hidden)
   and opencode (0.9); `ev_v2g_outage_schedule` is missed by all three on the public
   split — a verified shared blind spot (the optimum pre-charges an EV to serve more
   energy), not a specification defect.
