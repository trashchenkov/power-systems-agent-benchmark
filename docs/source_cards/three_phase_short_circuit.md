# Source card: three-phase short-circuit calculation

## Benchmark family

- Family: `three_phase_short_circuit`
- Candidate: `REL-TASK-033`
- Subdomain: protection, faults, and relay engineering
- Public case: `tasks/three_phase_short_circuit/public/case_001/task.json`

## Source basis

The task comes from the benchmark task bank entry for three-phase short-circuit current calculation. It is grounded in standard protection-engineering practice: represent the upstream network by a Thevenin or positive-sequence equivalent, sum source/transformer/line impedances on a common per-unit base, and compute the initial symmetrical RMS current.

Representative engineering references:

- IEC 60909 short-circuit calculation practice for initial symmetrical AC short-circuit currents.
- Power-system protection textbooks and utility calculation guides that use `I_k = U / (sqrt(3) * |Z_th|)` or the equivalent per-unit formula.
- The repository task-bank source: `literature/task_bank_v4_gap_fill_balanced.md#rel-task-033`.

## Operational instance

The public case gives:

- base apparent power, MVA;
- base line-to-line voltage, kV;
- positive-sequence source, transformer, and connection impedances in per unit;
- a small per-unit fault resistance.

The agent must calculate:

1. total positive-sequence impedance magnitude;
2. base current;
3. initial symmetrical three-phase short-circuit current in kA;
4. short-circuit apparent power in MVA.

## Evaluation logic

The evaluator independently recomputes the same quantities from the public inputs. It checks numeric fields within a small absolute/relative tolerance and rejects unknown answer fields. No expected answer is exposed in `task.json`.

## Limitations

This public case is deliberately compact: it does not model IEC voltage factors, X/R-dependent peak current, remote infeed, motor contribution, or full breaker duty. Those extensions are appropriate for hidden cases or future larger instances.
