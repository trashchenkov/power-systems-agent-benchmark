# Source card: breaker and relay short-circuit study

## Benchmark family

- Family: `breaker_relay_short_circuit`
- Candidate: `REL-TASK-045`
- Subdomain: protection, faults, and relay engineering
- Current implementation: executable public task with deterministic short-circuit and selection evaluator

## Source grounding

Primary local provenance:

- `literature/metadata/v4_balanced_core_shortlist.md`
- `literature/task_bank_v4_gap_fill_balanced.md#rel-task-045`

The selected task corresponds to a common protection engineering workflow: compute short-circuit currents at representative feeder locations, choose breaker interrupting capability, and set relay pickup so that it is above maximum load but sensitive to minimum fault current.

## Operational problem extracted

Given:

- line-to-line nominal voltage;
- source Thevenin impedance;
- transformer impedance;
- feeder impedance per km;
- near/mid/far fault locations;
- maximum load current;
- standard breaker ratings;
- breaker safety and relay sensitivity rules.

The solver must return:

- maximum 3-phase short-circuit current in kA;
- minimum 2-phase short-circuit current in kA;
- selected standard breaker interrupting rating in kA;
- relay pickup current in primary amperes.

## Benchmark adaptation

The public case uses a dependency-free balanced short-circuit approximation:

- `I_3ph = V_ll / (sqrt(3) * |Z_total|)`;
- `I_2ph = sqrt(3)/2 * I_3ph`.

This is intentionally simpler than a full IEC/ANSI short-circuit study, but it requires actual impedance accumulation and engineering selection logic rather than copying a stored answer.

## Evaluator

Evaluator module:

- `prototype/evaluators/evaluate_breaker_relay_short_circuit.py`

The evaluator independently computes the fault study and checks:

- reported maximum 3-phase current;
- reported minimum 2-phase current;
- breaker rating is a standard available rating;
- breaker rating exceeds fault current with safety factor;
- breaker rating is the smallest feasible standard rating;
- relay pickup is above load margin;
- relay pickup preserves minimum-fault sensitivity.

## Baseline

Baseline module:

- `baselines/breaker_relay_short_circuit/baseline.py`

The baseline computes the study, selects the smallest feasible breaker rating, and picks a midpoint relay pickup within the allowed sensitivity window.

## Limitations and next upgrades

- Current public case uses a simplified balanced approximation rather than IEC 60909 or ANSI momentary/asymmetrical duty.
- X/R asymmetry, DC offset, decrement, CT saturation, and time-current curves are not modelled yet.
- Hidden cases should add multiple voltage levels, transformer base conversions, zero/negative-sequence networks, and explicit relay curve coordination.
