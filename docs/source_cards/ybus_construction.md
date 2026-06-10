# Source card: Ybus construction from network data

## Benchmark family

- Family: `ybus_construction`
- Candidate: `REL-TASK-047`
- Subdomain: power-flow modelling and transmission analysis
- Current implementation: executable public task with deterministic evaluator

## Source grounding

Primary local provenance:

- `literature/metadata/v4_balanced_core_shortlist.md`
- `literature/task_bank_v4_gap_fill_balanced.md#rel-task-047`

The shortlisted task is the standard power-system modelling operation of constructing the bus admittance matrix from branch and shunt data. This is a prerequisite for Newton-Raphson power flow, DC/AC network analysis, fault calculations, and state estimation.

## Operational problem extracted

Given:

- ordered bus list;
- branch terminal buses;
- branch series impedance `r + jx` in per unit;
- total branch charging susceptance `b` in per unit;
- explicit bus shunts `g + jb`.

The solver must build the nodal admittance matrix `Ybus`:

- for each branch, compute `y = 1 / (r + jx)`;
- add `y + j*b/2` to both terminal diagonal entries;
- add `-y` to symmetric off-diagonal entries;
- add explicit shunts to their bus diagonal entries.

## Benchmark adaptation

The public case uses a three-bus transmission fragment with three lines and one shunt. The task is intentionally small enough to inspect by hand but requires complex arithmetic and matrix assembly rather than copying a hidden oracle.

The agent-facing packet contains the full input network and output schema. It does not contain `expected_submission`, `baseline_submission`, or evaluator-only fields.

## Evaluator

Evaluator module:

- `prototype/evaluators/evaluate_ybus_construction.py`

The evaluator independently recomputes `Ybus` from `task.network` and checks:

- required fields `buses` and `ybus`;
- exact bus order;
- square matrix shape;
- parseable complex entries represented as `{re, im}`;
- maximum complex absolute error within `numeric_tolerance`.

Metrics:

- `feasible`;
- `score`;
- `max_abs_error`;
- `entry_errors`.

## Baseline

Baseline module:

- `baselines/ybus_construction/baseline.py`

The baseline uses the same public formula, not a stored oracle, to produce a valid sample submission.

## Limitations and next upgrades

- The public task has no transformer taps or phase-shifters yet.
- The current evaluator assumes symmetric passive branches.
- Hidden cases should add off-nominal taps, multiple voltage levels, switched shunts, and larger sparse matrices.
- A later version can compare against pandapower/MATPOWER case conversion for external validation.
