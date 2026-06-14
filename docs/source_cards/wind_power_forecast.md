# Source card: wind_power_forecast

## Benchmark family

- Family: `wind_power_forecast`
- Candidate: `REL-TASK-009`
- Subdomain: forecasting & uncertainty
- Current implementation: executable public task with deterministic evaluator

## Primary source grounding

- Primary source: LoRA-Finetuned LLM for Multi-Step Wind Power Forecasting
- Locator: DOI:10.13140/RG.2.2.33696.34561
- Confidence: `medium`
- Private-library check: `local_archive_extracted/local_lit/power_engineering/LoRA-Finetuned-LLM-for-Multi-Step-Wind-Power-Forecasting.pdf`

Grounds multi-step wind-power forecasting; the case uses deterministic power-curve and residual-bias calculations.

## Derived traceability

- Task-bank entry: `literature/task_bank_v2_reliable_source_mining.md#rel-task-009`
- Task-bank role: derived task-bank entry only; it is not treated as the primary source.

## Benchmark adaptation

The public case is a compact executable instance derived from the primary method/source above. The source card documents provenance only; it does not change public inputs, formulas, evaluator logic, baselines, hard constraints, or sample submissions.

## Licensing note

Full books, standards, paywalled PDFs, and OCR text are not redistributed in this repository. Private-library paths above are provenance breadcrumbs for maintainers with legitimate access.
