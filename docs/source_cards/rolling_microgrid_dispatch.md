# Source card: rolling microgrid dispatch

## Benchmark family

- Family: `rolling_microgrid_dispatch`
- Candidate: `REL-TASK-026`
- Subdomain: microgrids and DER dispatch
- Public case: `tasks/rolling_microgrid_dispatch/public/case_001/task.json`

## Source basis

The task is based on short-horizon/rolling dispatch of renewable microgrids: every few minutes, the controller schedules diesel and storage setpoints from current forecasts while preserving battery SOC and avoiding unserved load.

Representative references:

- Rolling-horizon microgrid energy management.
- Battery-constrained DER dispatch with PV curtailment.
- Repository task-bank source: `literature/task_bank_v4_gap_fill_balanced.md#rel-task-026`.

## Evaluation logic

The evaluator uses the same deterministic optimization contract as the public task: enumerate feasible battery setpoints, simulate SOC and load balance over 5-minute intervals, choose the least-cost feasible schedule, and check the submitted dispatch.
