# Source card: EV/V2G outage scheduling

## Benchmark family

- Family: `ev_v2g_outage_schedule`
- Candidate: `REL-TASK-020`
- Subdomain: distribution systems and DER/EV
- Public case: `tasks/ev_v2g_outage_schedule/public/case_001/task.json`

## Source basis

This task models vehicle-to-grid support during a distribution outage. EVs provide critical-load energy subject to bidirectional charger power limits, efficiency, battery capacity, and reserve SOC constraints.

Representative references:

- V2G emergency/outage support and critical-load restoration scheduling.
- EV fleet SOC-constrained dispatch under uncertain event windows.
- Repository task-bank source: `literature/task_bank_v4_gap_fill_balanced.md#rel-task-020`.

## Evaluation logic

The evaluator enumerates feasible EV charge/discharge schedules over the outage window, simulates SOC with efficiency and reserve constraints, maximizes served critical-load energy, and checks dispatch, served energy, and final SOC.
