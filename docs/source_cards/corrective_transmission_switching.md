# Source card: corrective_transmission_switching

## Benchmark family

- Family: `corrective_transmission_switching`
- Candidate: `GAP-TASK-002`
- Subdomain: transmission operations, contingency & congestion management
- Current implementation: executable public task with deterministic evaluator

## Primary source grounding

- Primary source: Security Constrained Unit Commitment with Corrective Transmission Switching
- Locator: arXiv:2001.00597v1
- Confidence: `medium`
- Private-library check: `external_arxiv_not_in_private_pdf_corpus`

Primary source for post-contingency corrective switching; public case is a compact DC-flow adaptation, not the full SCUC MILP.

## Derived traceability

- Task-bank entry: `literature/task_bank_v4_gap_fill_balanced.md#gap-task-002`
- Task-bank role: derived task-bank entry only; it is not treated as the primary source.

## Benchmark adaptation

The public case is a compact executable instance derived from the primary method/source above. The source card documents provenance only; it does not change public inputs, formulas, evaluator logic, baselines, hard constraints, or sample submissions.

## Licensing note

Full books, standards, paywalled PDFs, and OCR text are not redistributed in this repository. Private-library paths above are provenance breadcrumbs for maintainers with legitimate access.
