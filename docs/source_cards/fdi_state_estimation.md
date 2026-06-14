# Source card: fdi_state_estimation

## Benchmark family

- Family: `fdi_state_estimation`
- Candidate: `GAP-TASK-006`
- Subdomain: OT cybersecurity, state estimation & bad data
- Current implementation: executable public task with deterministic evaluator

## Primary source grounding

- Primary source: Abur and Exposito, Power System State Estimation: Theory and Implementation
- Locator: largest-normalized-residual bad-data test
- Confidence: `high`
- Private-library check: `canonical_textbook_not_redistributed`

The executable case directly implements the textbook WLS/LNR bad-data identification method.

## Derived traceability

- Task-bank entry: `literature/task_bank_v4_gap_fill_balanced.md#gap-task-006`
- Task-bank role: derived task-bank entry only; it is not treated as the primary source.

## Benchmark adaptation

The public case is a compact executable instance derived from the primary method/source above. The source card documents provenance only; it does not change public inputs, formulas, evaluator logic, baselines, hard constraints, or sample submissions.

## Licensing note

Full books, standards, paywalled PDFs, and OCR text are not redistributed in this repository. Private-library paths above are provenance breadcrumbs for maintainers with legitimate access.
