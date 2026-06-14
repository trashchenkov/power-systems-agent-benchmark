# Source card: power_quality_event_classification

## Benchmark family

- Family: `power_quality_event_classification`
- Candidate: `GAP-TASK-008`
- Subdomain: power quality & standards
- Current implementation: executable public task with deterministic evaluator

## Primary source grounding

- Primary source: IEC 61000-4-30 / power-quality RMS event classification practice
- Locator: IEC 61000-4-30 measurement classes; sag/swell/interruption RMS thresholds
- Confidence: `high`
- Private-library check: `standard_not_redistributed`

The executable case directly applies standard power-quality event threshold categories to RMS windows.

## Derived traceability

- Task-bank entry: `literature/task_bank_v4_gap_fill_balanced.md#gap-task-008`
- Task-bank role: derived task-bank entry only; it is not treated as the primary source.

## Benchmark adaptation

The public case is a compact executable instance derived from the primary method/source above. The source card documents provenance only; it does not change public inputs, formulas, evaluator logic, baselines, hard constraints, or sample submissions.

## Licensing note

Full books, standards, paywalled PDFs, and OCR text are not redistributed in this repository. Private-library paths above are provenance breadcrumbs for maintainers with legitimate access.
