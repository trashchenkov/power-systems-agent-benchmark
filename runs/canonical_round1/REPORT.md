# Canonical evaluation round (2026-06)

The single consistent reference round used for the paper, run after all ten
specification defects, the harness isolation fix, the malformed-submission
robustness fix, and the transient-retry policy were in place. Three CLI agents,
identical prompts, 600 s per-case timeout, `--max-attempts 2`. Public uses the
committed `case_001` per family; hidden uses one generated `case_401` per family
from a fresh private seed (not recorded). Zero infrastructure-unresolved
failures; raw and retry-normalized metrics coincided (no retries fired).

## Final table

| agent (model) | public feasible | public perfect | public mean | hidden feasible | hidden perfect | hidden mean |
|---|---|---|---|---|---|---|
| codex (gpt-5.5 medium) | 40/41 | 36/41 | 0.971 | 40/41 | 37/41 | 0.969 |
| cursor (composer-2.5) | 39/41 | 35/41 | 0.947 | 40/41 | 36/41 | 0.969 |
| opencode (deepseek-v4-flash) | 37/41 | 35/41 | 0.900 | 38/41 | 35/41 | 0.920 |

`frt_compliance` hidden was rerun on a regenerated case after the generator fix
(`runs/canonical_round1/{agent}-frt-rerun/`); all three agents scored 1.0.
`fault_section_localization` hidden was re-scored against the fixed evaluator
without rerunning (the agents' original answers were correct).

## Findings

1. **The benchmark discriminates.** codex ≈ cursor (~0.97 mean) sit clearly
   above opencode (~0.90–0.92), consistently on both splits.

2. **Public and hidden are comparable on clean specifications.** For every
   agent the hidden score is within noise of public (slightly higher for two of
   three). The dramatic "ranking flip / public leader degrades most" observed in
   the earlier development round was an artifact of specification defects that
   disproportionately penalized cursor, not a genuine public/hidden difficulty
   gap. With clean specs the two splits agree on the ranking.

3. **The agent matrix found a latent evaluator physics bug.** Three agents
   independently localized the hidden `fault_section_localization` case to the
   physically correct section while the evaluator insisted on a different one,
   due to an off-by-one in the fault-current-indicator model (it placed the
   faulted section's downstream node on the fault path). This bug was invisible
   to the baseline-equals-evaluator self-consistency check — the baseline
   inherited the same error — and could only surface because independent agents
   applied the correct physics. This is the clearest demonstration of the
   agent-matrix quality-control methodology and is treated as a primary result.

4. **Quality-control loop, end to end.** Across the development and canonical
   rounds the *identical-failure-of-all-agents* criterion flagged, and we then
   fixed, ten specification defects plus the evaluator physics bug plus a
   generator ambiguity (a borderline-compliant FRT trace). Each fix was
   confirmed by rerun or by re-scoring existing submissions.

5. **Mild evidence against public-set contamination.** These are recent models
   and the public set is in an open repository; if the public cases were
   memorized we would expect public ≫ hidden. We observe public ≈ hidden. Either
   contamination is absent for these compact cases or they are too small to
   memorize usefully. Hidden evaluation's value here is therefore prospective —
   contamination resistance as the public set ages and models train on it —
   rather than a one-round difficulty gap.

## Per-agent remaining failures (clean round)

- codex public: `pv_volt_var`; hidden: `pv_volt_var`.
- cursor public: `pv_volt_var`, `transient_stability_prediction`; hidden:
  `operator_breaker_load_actions`.
- opencode public: `dispatch_uncertainty`, `pv_volt_var`,
  `distance_protection_settings`, `frt_compliance`(pre-fix env) ; hidden:
  `dispatch_uncertainty`, `distance_protection_settings`, `pv_volt_var`.

All remaining failures are genuine capability/quality differences (e.g.
`pv_volt_var` deep-excursion voltage control separates opencode/codex from
cursor); partial-credit penalties on `contingency_screening`, `flisr_restoration`,
`pf_voltage_repair` further separate agents.
