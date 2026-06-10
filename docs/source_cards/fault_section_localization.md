# Source card: fault-section localization from FCI states

## Benchmark family

- Family: `fault_section_localization`
- Candidate: `REL-TASK-052`
- Subdomain: distribution reliability and outage management
- Public case: `tasks/fault_section_localization/public/case_001/task.json`

## Source basis

This task models standard outage-management reasoning on radial feeders: upstream fault-current indicators identify the path to the fault, and downstream outage complaints identify the de-energized customer set.

Representative references:

- FCI-assisted fault section localization in radial distribution feeders.
- Outage-management systems that combine device telemetry and customer calls.
- Repository task-bank source: `literature/task_bank_v4_gap_fill_balanced.md#rel-task-052`.

## Evaluation logic

The evaluator tests every candidate section against observed FCI states and complaint nodes, selects the minimum-mismatch section, derives downstream affected customers, and checks the submitted structured answer.
