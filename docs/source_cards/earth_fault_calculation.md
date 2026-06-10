# Source card: earth-fault calculation by symmetrical components

## Benchmark family

- Family: `earth_fault_calculation`
- Candidate: `REL-TASK-034`
- Subdomain: protection, faults, and relay engineering
- Public case: `tasks/earth_fault_calculation/public/case_001/task.json`

## Source basis

The task is based on the standard symmetrical-components treatment of an A-phase-to-ground fault. For a single-line-to-ground fault with prefault voltage 1.0 per unit, the positive-, negative-, and zero-sequence networks are connected in series:

`I1 = I2 = I0 = 1 / (Z1 + Z2 + Z0 + 3 Zf)`.

The phase fault current and residual current are `3I0`.

Representative engineering references:

- Symmetrical-components chapters in power-system protection and fault-analysis textbooks.
- IEC/IEEE-style short-circuit calculation practice for unbalanced faults.
- Repository task-bank source: `literature/task_bank_v4_gap_fill_balanced.md#rel-task-034`.

## Operational instance

The public case gives:

- base apparent power and line-to-line voltage;
- positive-, negative-, and zero-sequence impedances in per unit;
- fault resistance in per unit;
- fault type: phase-to-ground fault.

The agent must return sequence current magnitudes and angles, plus the magnitude and angle of `3I0`.

## Evaluation logic

The evaluator independently computes the sequence-network denominator, converts per-unit currents to kA, and checks the submitted magnitudes and angles within tolerance. Unknown top-level answer keys are rejected.

## Limitations

The public instance uses a single compact Thevenin equivalent and ignores arc nonlinearity, mutual coupling, CT saturation, grounding-transformer details, and prefault load current. These are good candidates for hidden or later variants.
