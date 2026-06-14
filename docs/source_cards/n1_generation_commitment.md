# Source card: n1_generation_commitment

## Benchmark family

- Family: `n1_generation_commitment`
- Candidate: `GAP-TASK-001`
- Subdomain: markets, unit commitment, reserves & adequacy
- Current implementation: executable public task with deterministic evaluator

## Primary source grounding

- Primary source: Security Constrained Unit Commitment with Corrective Transmission Switching
- Locator: arXiv:2001.00597v1
- Confidence: `medium`
- Private-library check: `external_arxiv_not_in_private_pdf_corpus`

Primary source for N-1/security-constrained UC framing; case is a small deterministic commitment feasibility problem.

## Derived traceability

- Task-bank entry: `literature/task_bank_v4_gap_fill_balanced.md#gap-task-001`
- Task-bank role: derived task-bank entry only; it is not treated as the primary source.

## Benchmark adaptation

The public case is a compact executable instance derived from the primary method/source above. The source card documents provenance only; it does not change public inputs, formulas, evaluator logic, baselines, hard constraints, or sample submissions.

## Licensing note

Full books, standards, paywalled PDFs, and OCR text are not redistributed in this repository. Private-library paths above are provenance breadcrumbs for maintainers with legitimate access.
