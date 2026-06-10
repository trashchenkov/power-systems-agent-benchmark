# Source card: microgrid economic dispatch

## Benchmark family

- Family: `microgrid_economic_dispatch`
- Candidate: `REL-TASK-024`
- Subdomain: microgrids and DER dispatch
- Public case: `tasks/microgrid_economic_dispatch/public/case_001/task.json`

## Source basis

The task is based on standard microgrid economic dispatch: serve load using diesel generation, PV, and a battery while respecting generator and storage constraints and minimizing fuel/variable cost.

Representative references:

- Microgrid economic dispatch with DER and battery SOC constraints.
- Active-power balance and PV curtailment models used in microgrid scheduling.
- Repository task-bank source: `literature/task_bank_v4_gap_fill_balanced.md#rel-task-024`.

## Evaluation logic

The evaluator independently enumerates feasible battery setpoints, simulates SOC and balance constraints, selects the least-cost diesel schedule, and checks submitted per-period dispatch and total cost.
