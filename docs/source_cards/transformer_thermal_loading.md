# Source card: transformer_thermal_loading

## Benchmark family

- Family: `transformer_thermal_loading`
- Candidate: `CORE-SWAP-001`
- Subdomain: transmission operations & asset ratings
- Current implementation: executable public task with deterministic evaluator

## Primary source grounding

- Primary source: IEC 60076-7 transformer loading guide
- Locator: IEC 60076-7 top-oil / hot-spot exponential thermal model; IEEE C57.91 comparable practice
- Confidence: `high`
- Private-library check: `standard_not_redistributed`

The executable case directly implements the standard top-oil/hot-spot and ageing-factor method in compact form.

## Derived traceability

- Task-bank entry: `literature/task_bank_v2_reliable_source_mining.md#core-swap-001`
- Task-bank role: derived task-bank entry only; it is not treated as the primary source.

## Benchmark adaptation

The public case is a compact executable instance derived from the primary method/source above. The source card documents provenance only; it does not change public inputs, formulas, evaluator logic, baselines, hard constraints, or sample submissions.

## Licensing note

Full books, standards, paywalled PDFs, and OCR text are not redistributed in this repository. Private-library paths above are provenance breadcrumbs for maintainers with legitimate access.
