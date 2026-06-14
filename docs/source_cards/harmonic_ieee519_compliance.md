# Source card: harmonic_ieee519_compliance

## Benchmark family

- Family: `harmonic_ieee519_compliance`
- Candidate: `CORE-SWAP-003`
- Subdomain: power quality & standards
- Current implementation: executable public task with deterministic evaluator

## Primary source grounding

- Primary source: IEEE 519-2014 harmonic-control limits
- Locator: IEEE 519-2014 current-distortion and voltage-distortion limits
- Confidence: `high`
- Private-library check: `standard_not_redistributed`

The executable case directly applies IEEE-519-style TDD/THD limit-table logic; the standard is cited, not redistributed.

## Derived traceability

- Task-bank entry: `literature/task_bank_v2_reliable_source_mining.md#core-swap-003`
- Task-bank role: derived task-bank entry only; it is not treated as the primary source.

## Benchmark adaptation

The public case is a compact executable instance derived from the primary method/source above. The source card documents provenance only; it does not change public inputs, formulas, evaluator logic, baselines, hard constraints, or sample submissions.

## Licensing note

Full books, standards, paywalled PDFs, and OCR text are not redistributed in this repository. Private-library paths above are provenance breadcrumbs for maintainers with legitimate access.
