# Source card: critical_clearing_time

## Benchmark family

- Family: `critical_clearing_time`
- Candidate: `REL-TASK-048`
- Subdomain: stability & dynamics
- Current implementation: executable public task with deterministic evaluator

## Primary source grounding

- Primary source: Equal-area criterion for first-swing transient stability
- Locator: Kundur, Power System Stability and Control; also supported by Glover/Overbye/Sarma stability-program discussion
- Confidence: `high`
- Private-library check: `local_archive_extracted/local_lit/power_engineering/J. Duncan Glover, Thomas J. Overbye, Mulukutla S. Sarma - Power System Analysis and Design-Cengage Learning (2017).pdf`

Canonical equal-area method; the executable case directly computes critical angle/time from the stated swing-equation parameters.

## Derived traceability

- Task-bank entry: `literature/task_bank_v2_reliable_source_mining.md#rel-task-048`
- Task-bank role: derived task-bank entry only; it is not treated as the primary source.

## Benchmark adaptation

The public case is a compact executable instance derived from the primary method/source above. The source card documents provenance only; it does not change public inputs, formulas, evaluator logic, baselines, hard constraints, or sample submissions.

## Licensing note

Full books, standards, paywalled PDFs, and OCR text are not redistributed in this repository. Private-library paths above are provenance breadcrumbs for maintainers with legitimate access.
