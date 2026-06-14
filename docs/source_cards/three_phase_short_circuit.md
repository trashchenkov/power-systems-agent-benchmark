# Source card: three_phase_short_circuit

## Benchmark family

- Family: `three_phase_short_circuit`
- Candidate: `REL-TASK-033`
- Subdomain: protection, faults & relay engineering
- Current implementation: executable public task with deterministic evaluator

## Primary source grounding

- Primary source: IEC 60909 equivalent-voltage-source short-circuit calculation
- Locator: IEC 60909 max/min three-phase short-circuit current method
- Confidence: `high`
- Private-library check: `standard_not_redistributed; also local relay-protection worked examples`

The executable case directly applies IEC-60909-style max/min short-circuit current calculations.

## Derived traceability

- Task-bank entry: `literature/task_bank_v2_reliable_source_mining.md#rel-task-033`
- Task-bank role: derived task-bank entry only; it is not treated as the primary source.

## Benchmark adaptation

The public case is a compact executable instance derived from the primary method/source above. The source card documents provenance only; it does not change public inputs, formulas, evaluator logic, baselines, hard constraints, or sample submissions.

## Licensing note

Full books, standards, paywalled PDFs, and OCR text are not redistributed in this repository. Private-library paths above are provenance breadcrumbs for maintainers with legitimate access.
