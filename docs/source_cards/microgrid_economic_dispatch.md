# Source card: microgrid_economic_dispatch

## Benchmark family

- Family: `microgrid_economic_dispatch`
- Candidate: `REL-TASK-024`
- Subdomain: microgrids & DER dispatch
- Current implementation: executable public task with deterministic evaluator

## Primary source grounding

- Primary source: Microgrid economic-dispatch source from local archive
- Locator: local archive fmincon / microgrid dispatch source
- Confidence: `medium`
- Private-library check: `local_archive_extracted/local_lit/power_engineering/fmincon.pdf`

Grounds constrained microgrid dispatch; the task implements an explicit diesel/PV/battery cost-minimization instance.

## Derived traceability

- Task-bank entry: `literature/task_bank_v2_reliable_source_mining.md#rel-task-024`
- Task-bank role: derived task-bank entry only; it is not treated as the primary source.

## Benchmark adaptation

The public case is a compact executable instance derived from the primary method/source above. The source card documents provenance only; it does not change public inputs, formulas, evaluator logic, baselines, hard constraints, or sample submissions.

## Licensing note

Full books, standards, paywalled PDFs, and OCR text are not redistributed in this repository. Private-library paths above are provenance breadcrumbs for maintainers with legitimate access.
