# Source card: islanded microgrid P/Q dispatch

## Benchmark family

- Family: `islanded_microgrid_pq_dispatch`
- Candidate: `REL-TASK-022`
- Subdomain: microgrids and DER dispatch
- Public case: `tasks/islanded_microgrid_pq_dispatch/public/case_001/task.json`

## Source basis

The task is based on islanded microgrid active/reactive dispatch: a diesel unit and grid-forming inverter must balance P/Q demand, respect inverter apparent-power capability, and maintain voltage within an acceptable range.

Representative references:

- Islanded microgrid P/Q balancing and inverter capability curves.
- Voltage support through reactive power in low-voltage microgrids.
- Repository task-bank source: `literature/task_bank_v4_gap_fill_balanced.md#rel-task-022`.

## Evaluation logic

The evaluator independently uses available inverter active power first, allocates reactive power within the inverter capability circle, computes diesel P/Q, voltage from the public sensitivity model, and total operating cost. Submitted structured values are checked with numeric tolerance.
