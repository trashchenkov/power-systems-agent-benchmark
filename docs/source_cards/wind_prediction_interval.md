# Source card: wind_prediction_interval

## Benchmark family

- Family: `wind_prediction_interval`
- Candidate: `REL-TASK-012`
- Current implementation: executable public task with deterministic evaluator

## Primary source grounding

- Primary source: Benyamin Khorramdel, C. Y. Chung, Nima Safari, G. C. D. Price, A Fuzzy Adaptive Probabilistic Wind Power Prediction Framework Using Diffusion Kernel Density Estimators, IEEE Transactions on Power Systems, 2018
- Locator: DOI:10.1109/TPWRS.2018.2848207; local OCR Advanced Prediction... lines 603-633 cite PI reliability/sharpness and this paper
- Confidence: `medium`
- Verification status: `doi_resolved_crossref; local slides cite the resolved source`
- Private-library breadcrumb: `local_archive_extracted/local_lit/power_engineering/Advanced Prediction Techniques Applied to Smart Grids.pdf`

Replaces vague prediction-interval slide locator with DOI-resolved IEEE TPWRS source for wind-power probabilistic prediction intervals.

## DOI / locator verification

- DOI-bearing locators above were checked against Crossref, DataCite, and/or OpenAlex during the follow-up audit where applicable.
- Vague local-archive labels such as `local archive ... sections` are no longer used as medium-confidence primary locators.
- If a source could not be resolved to a specific bibliographic item that fully grounds the benchmark family, the family is marked `low` rather than upgraded by local-library presence alone.

## Derived traceability

- Task-bank entry: `literature/task_bank_v2_reliable_source_mining.md#rel-task-012`
- Task-bank role: derived task-bank entry only; it is not treated as the primary source.

## Benchmark adaptation

The public case is a compact executable instance derived from the primary method/source above. The source card documents provenance only; it does not change public inputs, formulas, evaluator logic, baselines, hard constraints, or sample submissions.

## Licensing note

Full books, standards, paywalled PDFs, and OCR text are not redistributed in this repository. Private-library paths above are provenance breadcrumbs for maintainers with legitimate access.
