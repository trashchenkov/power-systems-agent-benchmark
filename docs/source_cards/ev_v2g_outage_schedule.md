# Source card: ev_v2g_outage_schedule

## Benchmark family

- Family: `ev_v2g_outage_schedule`
- Candidate: `REL-TASK-020`
- Subdomain: distribution systems & DER/EV
- Current implementation: executable public task with deterministic evaluator

## Primary source grounding

- Primary source: The Role of Electrical Vehicles for Power Quality and Security during Outages in the Distribution Grid
- Locator: DOI:10.1109/RTUCON51174.2020.9316604
- Confidence: `medium`
- Private-library check: `local_archive_extracted/local_lit/power_engineering/TheRoleofElectricalVehiclesforPowerQualityandSecurityduringOutagesintheDistributionGrid_final.pdf`

Grounds EV/V2G outage-support scheduling; the task uses explicit energy/SOC constraints.

## Derived traceability

- Task-bank entry: `literature/task_bank_v2_reliable_source_mining.md#rel-task-020`
- Task-bank role: derived task-bank entry only; it is not treated as the primary source.

## Benchmark adaptation

The public case is a compact executable instance derived from the primary method/source above. The source card documents provenance only; it does not change public inputs, formulas, evaluator logic, baselines, hard constraints, or sample submissions.

## Licensing note

Full books, standards, paywalled PDFs, and OCR text are not redistributed in this repository. Private-library paths above are provenance breadcrumbs for maintainers with legitimate access.
