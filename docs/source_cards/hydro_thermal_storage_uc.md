# Source card: hydro_thermal_storage_uc

## Benchmark family

- Family: `hydro_thermal_storage_uc`
- Candidate: `GAP-TASK-013`
- Subdomain: generation scheduling: hydro, thermal & storage
- Current implementation: executable public task with deterministic evaluator

## Primary source grounding

- Primary source: Unit-commitment sources for microgrids and ADMM UC
- Locator: arXiv:2012.07118v1; arXiv:2311.13438v1
- Confidence: `medium`
- Private-library check: `external_arxiv_not_in_private_pdf_corpus`

Grounds UC with emissions/ramping constraints; hydro/storage terms are compact benchmark extensions.

## Derived traceability

- Task-bank entry: `literature/task_bank_v4_gap_fill_balanced.md#gap-task-013`
- Task-bank role: derived task-bank entry only; it is not treated as the primary source.

## Benchmark adaptation

The public case is a compact executable instance derived from the primary method/source above. The source card documents provenance only; it does not change public inputs, formulas, evaluator logic, baselines, hard constraints, or sample submissions.

## Licensing note

Full books, standards, paywalled PDFs, and OCR text are not redistributed in this repository. Private-library paths above are provenance breadcrumbs for maintainers with legitimate access.
