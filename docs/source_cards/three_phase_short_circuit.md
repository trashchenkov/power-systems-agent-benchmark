# Source card: three-phase short-circuit calculation

## Benchmark family

- Family: `three_phase_short_circuit`
- Candidate: `REL-TASK-033`
- Subdomain: protection, faults, and relay engineering
- Public case: `tasks/three_phase_short_circuit/public/case_001/task.json`

## Source basis

The task comes from the benchmark task bank entry for three-phase short-circuit current calculation. It is grounded in IEC 60909 equivalent-voltage-source practice: represent the upstream network by a positive-sequence equivalent, sum source/transformer/line impedances on a common per-unit base, and compute the canonical max/min current pair `I_k = c * Un / (sqrt(3) * |Z_k|)`:

- maximum current with `c_max = 1.10` (medium voltage) and a bolted fault — fault resistance is neglected because it would non-conservatively lower the equipment-rating current;
- minimum current with `c_min = 1.00` and the published fault/contact resistance included — the protection-sensitivity current.

Representative engineering references:

- IEC 60909-0 equivalent-voltage-source method, voltage-factor table (c_max/c_min), and the max/min calculation split.
- Power-system protection textbooks and utility calculation guides using the equivalent per-unit formula.
- The repository task-bank source: `literature/task_bank_v4_gap_fill_balanced.md#rel-task-033`.

## Operational instance

The public case gives:

- base apparent power, MVA;
- base line-to-line voltage, kV;
- positive-sequence source, transformer, and connection impedances in per unit;
- a small per-unit fault resistance.

The agent must calculate:

1. bolted positive-sequence impedance magnitude and the magnitude including fault resistance;
2. base current;
3. maximum initial symmetrical current (c_max, bolted) in kA and the corresponding short-circuit apparent power in MVA;
4. minimum current (c_min, fault resistance included) in kA.

## Evaluation logic

The evaluator independently recomputes the same quantities from the public inputs. It checks numeric fields within a small absolute/relative tolerance and rejects unknown answer fields. No expected answer is exposed in `task.json`.

## Limitations

This public case is deliberately compact: it does not model X/R-dependent peak current (kappa factor), breaking/thermal currents, transformer/generator impedance correction factors, remote infeed, or motor contribution. Those extensions are appropriate for hidden cases or future larger instances.
