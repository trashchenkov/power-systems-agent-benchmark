# Source card: microgrid_economic_dispatch

## Benchmark family

- Family: `microgrid_economic_dispatch`
- Candidate: `REL-TASK-024`
- Current implementation: executable public task with deterministic evaluator

## Primary source grounding

- Primary source: Nohora España, John Barco-Jiménez, Andrés Pantoja, Nicanor Quijano, Distributed population dynamics for active and reactive power dispatch in islanded microgrids, International Journal of Electrical Power & Energy Systems, 2021
- Locator: DOI:10.1016/j.ijepes.2020.106407; local OCR fmincon_78640f47.txt lines 42-65, 110-118
- Confidence: `medium`
- Verification status: `doi_resolved_crossref; found in private library`
- Private-library breadcrumb: `local_archive_extracted/local_lit/power_engineering/fmincon.pdf`

Resolved fmincon.pdf to the underlying microgrid dispatch paper; public case is a compact cost-minimization adaptation.

## DOI / locator verification

- DOI-bearing locators above were checked against Crossref, DataCite, and/or OpenAlex during the follow-up audit where applicable.
- Vague local-archive labels such as `local archive ... sections` are no longer used as medium-confidence primary locators.
- If a source could not be resolved to a specific bibliographic item that fully grounds the benchmark family, the family is marked `low` rather than upgraded by local-library presence alone.

## Derived traceability

- Task-bank entry: `literature/task_bank_v2_reliable_source_mining.md#rel-task-024`
- Task-bank role: derived task-bank entry only; it is not treated as the primary source.

## Benchmark adaptation

The public case is a compact executable instance derived from the primary method/source above. The source card documents provenance only; it does not change public inputs, formulas, evaluator logic, baselines, hard constraints, or sample submissions.

## Licensing note

Full books, standards, paywalled PDFs, and OCR text are not redistributed in this repository. Private-library paths above are provenance breadcrumbs for maintainers with legitimate access.
