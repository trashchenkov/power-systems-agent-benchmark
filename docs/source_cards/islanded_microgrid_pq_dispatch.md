# Source card: islanded_microgrid_pq_dispatch

## Benchmark family

- Family: `islanded_microgrid_pq_dispatch`
- Candidate: `REL-TASK-022`
- Subdomain: microgrids & DER dispatch
- Current implementation: executable public task with deterministic evaluator

## Primary source grounding

- Primary source: Distributed active/reactive dispatch in isolated microgrids
- Locator: local archive fmincon / microgrid dispatch source
- Confidence: `medium`
- Private-library check: `local_archive_extracted/local_lit/power_engineering/fmincon.pdf`

Grounds joint P/Q dispatch with inverter capability; the task uses explicit balance, voltage-sensitivity and capability constraints.

## Derived traceability

- Task-bank entry: `literature/task_bank_v2_reliable_source_mining.md#rel-task-022`
- Task-bank role: derived task-bank entry only; it is not treated as the primary source.

## Benchmark adaptation

The public case is a compact executable instance derived from the primary method/source above. The source card documents provenance only; it does not change public inputs, formulas, evaluator logic, baselines, hard constraints, or sample submissions.

## Licensing note

Full books, standards, paywalled PDFs, and OCR text are not redistributed in this repository. Private-library paths above are provenance breadcrumbs for maintainers with legitimate access.
