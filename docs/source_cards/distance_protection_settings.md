# Source card: distance protection settings

## Benchmark family

- Family: `distance_protection_settings`
- Candidate: `REL-TASK-039`
- Subdomain: protection, faults, and relay engineering
- Current implementation: executable public task with deterministic reach/time coordination evaluator

## Source grounding

Primary local provenance:

- `literature/metadata/v4_balanced_core_shortlist.md`
- `literature/task_bank_v4_gap_fill_balanced.md#rel-task-039`

The selected task corresponds to the common relay-engineering operation of choosing distance protection zones for medium/high-voltage lines. Standard practice uses an instantaneous underreaching Zone 1, delayed Zone 2 for protected-line plus adjacent-line backup, and delayed Zone 3 for remote backup while avoiding load encroachment.

## Operational problem extracted

Given:

- protected-line positive-sequence impedance per km and length;
- adjacent remote backup line impedances;
- maximum load apparent power;
- configurable reach and delay coordination windows.

The solver must return:

- `zone1_ohm`, `zone2_ohm`, `zone3_ohm` in primary ohms;
- `zone1_delay_s`, `zone2_delay_s`, `zone3_delay_s` in seconds.

## Benchmark adaptation

The public case uses a 110 kV protected line with two downstream/remote backup lines. The evaluator uses impedance magnitudes rather than a full R-X polygon/mho characteristic. This keeps the MVP dependency-free while still requiring actual relay-setting calculations rather than copying a stored answer.

## Evaluator

Evaluator module:

- `prototype/evaluators/evaluate_distance_protection_settings.py`

The evaluator independently computes:

- protected-line impedance magnitude;
- shortest and longest backup-line impedance magnitudes;
- Zone 1 underreach window;
- Zone 2 backup-reach window;
- Zone 3 remote-backup window;
- load-encroachment ceiling using `V_kV^2 / S_MVA`;
- timing coordination windows.

It checks:

- all fields present and numeric;
- Zone 1/2/3 reach windows;
- strictly increasing reaches;
- delay windows;
- nondecreasing time coordination.

## Baseline

Baseline module:

- `baselines/distance_protection_settings/baseline.py`

The baseline selects midpoint reach values inside each allowed window and minimum coordinated delays.

## Limitations and next upgrades

- Current public case uses scalar impedance magnitude, not directional/mho/quadrilateral R-X characteristics.
- Mutual coupling, infeed, fault resistance, CT/VT errors, and zero-sequence compensation are not modelled yet.
- Hidden cases should add multi-terminal lines, infeed factors, zero-sequence compensation, and explicit R-X load-encroachment checks.
