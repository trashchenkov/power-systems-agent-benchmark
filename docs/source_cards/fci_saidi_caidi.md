# Source card: SAIDI/CAIDI impact of FCI deployment

## Benchmark family

- Family: `fci_saidi_caidi`
- Candidate: `REL-TASK-053`
- Subdomain: distribution reliability and outage management
- Public case: `tasks/fci_saidi_caidi/public/case_001/task.json`

## Source basis

This task uses standard reliability-index definitions to quantify how FCI-driven restoration-time reductions affect SAIDI and CAIDI.

Representative references:

- Standard SAIDI, SAIFI, and CAIDI definitions for distribution reliability.
- FCI deployment studies that reduce fault location and restoration time.
- Repository task-bank source: `literature/task_bank_v4_gap_fill_balanced.md#rel-task-053`.

## Evaluation logic

The evaluator computes baseline customer-minutes and customer interruptions, applies best deployed-FCI restoration-time reductions subject to a minimum duration floor, recomputes SAIDI/CAIDI/SAIFI, and checks the reported improvements.
