# Source card: FCI placement for patrol-time reduction

## Benchmark family

- Family: `fci_placement`
- Candidate: `REL-TASK-051`
- Subdomain: distribution reliability and outage management
- Public case: `tasks/fci_placement/public/case_001/task.json`

## Source basis

This task models FCI planning as a budgeted placement problem that maximizes expected customer-weighted patrol-time savings across feeder fault sections.

Representative references:

- Distribution fault indicator placement for reliability improvement.
- Customer-interruption-minute objective functions for outage management investments.
- Repository task-bank source: `literature/task_bank_v4_gap_fill_balanced.md#rel-task-051`.

## Evaluation logic

The evaluator enumerates all candidate sets of the requested size, computes each section's best patrol-time reduction from selected devices, maximizes annual fault-rate × customers × minutes saved, and checks the selected set and objective accounting.
