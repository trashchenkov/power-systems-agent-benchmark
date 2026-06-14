# Source card: dynamic_thermal_rating

## Benchmark family

- Family: `dynamic_thermal_rating`
- Candidate: `REL-TASK-014`
- Current implementation: executable public task with deterministic evaluator

## Primary source grounding

- Primary source: N. Safari, S. M. Mazhari, C. Y. Chung, S. B. Ko, Secure Probabilistic Prediction of Dynamic Thermal Line Rating, Journal of Modern Power Systems and Clean Energy, 2022
- Locator: DOI:10.35833/mpce.2020.000641; local OCR Advanced Prediction... lines 640-749 cites RTTR heat balance/weather factors and this paper
- Confidence: `medium`
- Verification status: `doi_resolved_crossref; local slides cite the resolved source`
- Private-library breadcrumb: `local_archive_extracted/local_lit/power_engineering/Advanced Prediction Techniques Applied to Smart Grids.pdf`

Replaces vague dynamic-line-rating slide locator with a DOI-resolved MPCE article plus local slide cross-reference; benchmark remains a compact heat-balance surrogate.

## DOI / locator verification

- DOI-bearing locators above were checked against Crossref, DataCite, and/or OpenAlex during the follow-up audit where applicable.
- Vague local-archive labels such as `local archive ... sections` are no longer used as medium-confidence primary locators.
- If a source could not be resolved to a specific bibliographic item that fully grounds the benchmark family, the family is marked `low` rather than upgraded by local-library presence alone.

## Derived traceability

- Task-bank entry: `literature/task_bank_v2_reliable_source_mining.md#rel-task-014`
- Task-bank role: derived task-bank entry only; it is not treated as the primary source.

## Benchmark adaptation

The public case is a compact executable instance derived from the primary method/source above. The source card documents provenance only; it does not change public inputs, formulas, evaluator logic, baselines, hard constraints, or sample submissions.

## Licensing note

Full books, standards, paywalled PDFs, and OCR text are not redistributed in this repository. Private-library paths above are provenance breadcrumbs for maintainers with legitimate access.
