# FINDINGS.md

## Current answer

A credible benchmark for power-systems agents should be tiered and executable, not just QA. The likely MVP should use a Python-first deterministic substrate such as pandapower for PF/OPF/contingency tasks, while the broader benchmark can add Grid2Op for sequential operation, OpenDSS for distribution/DER, PowerModels/PGLib for rigorous OPF, ANDES for dynamics, and PyPSA for planning/dispatch.

## What works

- PowerAgentBench gives the closest existing LLM/tool-agent pattern for physical power-system tasks.
- Grid2Op/L2RPN gives a mature sequential grid-operation environment, but mostly RL-oriented.
- pandapower is the most convenient MVP substrate for Python-native deterministic tasks.
- The task design should separate: simulator substrate, agent interface, hidden evaluator, scoring metrics, and evidence/logging.

## What does not work / likely weak directions

- A pure text QA benchmark would not satisfy the power-systems substrate requirement.
- One simulator cannot credibly cover all power-systems domains.
- Live API/data benchmarks are interesting but reduce reproducibility for a core benchmark.

## Open directions

- Deep inspect PowerAgentBench task/evaluator design.
- Build candidate task taxonomy with exact input/output contracts.
- Decide MVP: pandapower-first vs Grid2Op-first.
- Define hidden tests/randomized cases without making results irreproducible.

## Next levers

1. Narrow verification: read PowerAgentBench evaluator and task specs.
2. Orthogonal source family: inspect simulator examples and case libraries.
3. Structural reframe: define benchmark tiers by substrate and capability.

## PowerAgentBench inspection update

PowerAgentBench should be treated as the closest reference design. Copy the benchmark mechanics, not necessarily the code: public/hidden split, hidden recomputation, tool APIs, budgeted validation, evidence metrics, scripted baselines. Differentiate by broader task taxonomy, pandapower-first AC MVP, and simulator-agnostic schema.

## Direction update — literature-derived task bank

The stronger strategy is to first mine a broad, current power-systems literature/manual corpus into a large task bank, then normalize tasks into executable benchmark families. This avoids merely reproducing PowerAgentBench's steady-state security tasks. Proprietary tools such as DIgSILENT PowerFactory should be used as sources of realistic workflows, not as mandatory open benchmark substrates unless a separate licensed track is intended.

## Source intake update — Drive folder 16KL

The provided Google Drive link is accessible. Whole-folder download is not a good strategy: the root contains a very broad Documents tree with many unrelated files. Partial download produced 23 files / 48.5 MB; inventory saved at `literature/metadata/gdrive_16KL_inventory.md`. For the benchmark literature corpus, use either narrower Drive subfolder links or selective filtering by filenames/paths such as pandapower, DIgSILENT, PowerFactory, OpenDSS, load flow, OPF, contingency, stability, reliability, protection, distribution, microgrid.

## Deep source intake update — Drive folder 16KL

Recursive no-download listing succeeded for the full nested folder tree: 8,439 downloadable files. Deep listing artifacts are saved at `literature/metadata/gdrive_16KL_deep_listing.json`, `literature/metadata/gdrive_16KL_deep_inventory.md`, and `literature/metadata/gdrive_16KL_deep_inventory.json`. The useful material is indeed deep in nested folders, especially under `мероприятия/Эстония/стажировка/microgrid/` with FTA/PVS/DG/DISTR/grid artifacts, `related papers`, `reliability data`, `method`, and `structure`, plus course PDFs under the nested Fax/выкладка tree. Prioritize selective downloads from these subtrees rather than root-wide download.

## Selective Drive corpus update — 16KL + 1BlfnGI

Selective download completed for the two most accessible Drive source trees. The curated corpus is at `literature/curated_drive_corpus` and contains 202 selected files / ~438 MB: 109 files from `16KL` and 93 from `1BlfnGI`. The manifest is `literature/metadata/selected_drive_download_manifest.json`; the successful direct-download report is `literature/metadata/selected_drive_download_report_requests.json`. The second folder `0B-VEp_l82QO3N2hOdXJ2dnBfcGc` is browser-accessible but gdown folder listing returns 401; visible top-level folders include risk analysis, power-plant safety, Petri nets, DR, Matlab/Simulink, and theory/modeling, so it should be scraped selectively via browser/Drive HTML if needed.

## Local archive intake update — Sergey literature archive

The user-provided Google Drive archive was downloaded as `literature/local_archive_intake/power_engineering_cleaned_20260608_095416.zip` (459 MB Google Drive label, 481,642,708 bytes locally). Zip integrity check passed. Because filenames were stored as UTF-8 without the zip UTF-8 flag and some names were too long, extraction used a custom safe extractor with UTF-8 filename recovery and component shortening. Extracted corpus is at `literature/local_archive_extracted/local_lit`: 266 archive entries total, 135 real files after excluding `__MACOSX` resource forks, 562,870,030 bytes. Clean inventory is `literature/metadata/local_archive_clean_inventory.md`; full extracted inventory is `literature/metadata/local_archive_extracted_inventory.json`.

High-value additions from the local archive include: ElecBench / power dispatch benchmark paper; PowerFactory converter-dominated systems book; Power System Analysis and Design; multiple relay protection textbooks and course materials; smart grid / PV / renewable verification materials; faulted-circuit indicators and reliability material; and Sergey-authored/related benchmark design note `Отраслевые_агентные_бенчмарки_и_проектирование_benchmark_для_электроэнергетики.pdf`. This archive is more concentrated and immediately useful than the broad Drive roots; prioritize it for literature mining and task-bank extraction.

## Task-bank mining update — local archive first pass

A first mining pass over 13 high-value local-archive documents extracted ~692k characters of text to `literature/extracted_text/local_archive_first_mining` and produced `literature/task_bank_v0_from_local_archive.md`. The resulting bank contains 22 executable benchmark task families. Recommended MVP slice: (1) pandapower AC load-flow correction / voltage repair, (2) dispatch/OPF under forecast uncertainty, (3) N-1 contingency assessment and mitigation, (4) FCI reliability impact and placement, (5) inverse-time overcurrent relay coordination, and (6) DER/EV voltage support in distribution feeders. This gives a practical first benchmark that is executable without proprietary software but grounded in PowerFactory/relay/reliability/DER literature.

## Benchmark spec/prototype update — v0 executable skeleton

The MVP task-bank was converted into `benchmark_spec_v0.md` plus a minimal executable prototype layout. Current artifacts: `schemas/task.schema.json`, public task cases under `tasks/`, a dependency-free voltage-repair evaluator at `prototype/evaluators/evaluate_voltage_repair.py`, smoke tests under `tests/`, and artifact validation at `scripts/validate_benchmark_artifacts.py`. Verification passed with `python -m unittest discover -v`, `python scripts/validate_benchmark_artifacts.py`, and the public voltage evaluator command. Next technical step is to pin/install simulator dependencies and replace the linear voltage surrogate with a real `pandapower` hidden evaluator for AC load-flow correction.

## Packaging update — skill vs benchmark repo

`PACKAGING_STRATEGY.md` records the recommended split. Use `trashchenkov/hermes-autoinvestigation-skill` as the reusable research/task-mining workflow layer, not as the runnable benchmark package. The executable benchmark should become a separate repo containing `tasks/`, `schemas/`, `prototype/evaluators/`, tests, dependency files, CI, docs, and baselines. Added `README.md`, `pyproject.toml`, `.github/workflows/check.yml`, and `scripts/check.sh`; `./scripts/check.sh` passes locally. Do not push/create a remote without explicit target-repo confirmation.

## Repository scaffold update — publishable draft shape

The benchmark scaffold now has repo-level files (`README.md`, `LICENSE`, `.gitignore`, `pyproject.toml`, CI draft), docs (`docs/evaluator_contract.md`, `docs/public_hidden_split.md`, `docs/metrics.md`), schemas (`task`, `submission`, `evaluation-result`), baseline placeholder, and `HANDOFF.md`. The autoinvestigation ledgers were updated with the prototype-phase scope, packaging claims, and completed threads. Current local quality gate: `./scripts/check.sh` passes and validates 2 task artifacts, 11 required repo files, and 3 schema files.

## Full local archive task-mining update — literature-first v1

At the user's request, task mining was expanded from the 13-document first pass to all downloaded local-archive documents under `literature/local_archive_extracted/local_lit/power_engineering`. Coverage: 127 discovered PDFs/DOCX, 124 successfully text-extracted, 17,712,021 extracted characters. Artifacts: `literature/metadata/all_local_archive_extraction_report.json`, `literature/extracted_text/all_local_archive/`, `literature/metadata/all_local_archive_task_snippets.json`, `literature/metadata/all_local_archive_source_triage.md`, and `literature/task_bank_v1_literature_derived.md`. The v1 bank contains 37 provenance-linked candidates, including strong sources for anti-icing conductor heating optimization, smart-inverter Volt-VAR voltage control, ElecBench dispatch, FCI reliability/placement, relay coordination, zero-sequence ground-fault identification, EV/V2G outage support, and wind forecasting. A bibliography/task table with OpenAlex citation counts was added at `literature/metadata/local_archive_bibliography_task_table.csv` and `.md`; note that `статья Бандурин №102 исправленная.docx` is user-confirmed to be a copy of a published article, while OpenAlex found no indexed citations in this pass. Next step should be promoting a small shortlist into exact `literature_cards/` with quotes/page-line locators and then executable task contracts.

## Reliable-source task mining pass

- Added `literature/task_bank_v2_reliable_source_mining.md`: 62 task candidates mined from accepted-match or web-confirmed sources.
- Added machine-readable indexes: `literature/metadata/reliable_source_task_candidates_v2.json` and `.csv`.
- Strongest immediate implementation families: pandapower/MATPOWER core, protection formula engine, FCI graph tasks, EV/V2G feeder support, forecasting/UQ, and MAS control/restoration tasks.

## Domain-only balanced task bank v3

- Added `literature/task_bank_v3_domain_only_balanced.md`: excludes benchmark-derived core tasks and keeps 61 primary domain-source candidates.
- Added coverage artifacts: `literature/metadata/domain_only_task_candidates_v3.json`, `.csv`, and `literature/metadata/subdomain_coverage_matrix_v3.md`.
- Current balanced shortlist: 37 tasks. Key imbalance: protection is overrepresented (17 candidates), while markets/unit commitment, asset management, OT cybersecurity, power quality, and broader transmission operations need more primary-domain sources.

## Gap-fill balanced task bank v4

- Added `literature/task_bank_v4_gap_fill_balanced.md`: targeted gap-fill for undercovered energy subdomains using arXiv/domain primary sources plus clearly marked low-confidence local gap signals.
- Added `literature/metadata/v4_balanced_core_shortlist.md`: 41-task quota-balanced core shortlist from 75 total domain-only candidates.
- Added source/metadata files: `gap_fill_arxiv_sources.json`, `gap_fill_task_candidates_v4.json`, `domain_task_candidates_v4_combined.json/.csv`, and `subdomain_coverage_matrix_v4.md`.
- `REL-TASK-062` / ElecBench-derived task remains excluded. Placeholder tasks `GAP-TASK-010` asset/RUL and `GAP-TASK-014` price forecasting are not in core until better primary sources are mined.

## Bilingual v0 executable slice

- Added bilingual v0 slice artifacts: `literature/v0_executable_benchmark_slice.ru.md` and `literature/v0_executable_benchmark_slice.en.md`, with index `literature/v0_executable_benchmark_slice.md`.
- The slice freezes 7 executable task families: AC PF voltage repair, N-1 contingency screening, FLISR restoration, overcurrent protection settings, PV Volt-VAR, false-data injection detection, and FRT/grid-code compliance.
- Each task family includes explicit source provenance, substrate, public input / agent output, hidden evaluator, baseline, and first implementation target.
- Policy captured: externally-facing planning artifacts for this benchmark should be bilingual RU/EN and include task sources.

## v0 implementation start — bilingual plan and source provenance gate

- Added bilingual implementation plans: `docs/plans/v0-executable-benchmark.ru.md` and `docs/plans/v0-executable-benchmark.en.md`, with index `docs/plans/v0-executable-benchmark.md`.
- Started implementation with strict TDD. Added `tests/test_artifact_validation.py` first, watched it fail on missing `validate_task_data`, then implemented structured `source_provenance` validation.
- Updated `schemas/task.schema.json` and existing task artifacts so every task must include structured source provenance (`title`, `locator`, `confidence`, `notes`) in addition to legacy `source_evidence`.
- Added a public greedy baseline for `pf_voltage_repair` at `baselines/pf_voltage_repair/baseline.py` after a RED test in `tests/test_voltage_repair_baseline.py`.
- Verification: `./scripts/check.sh` passes: 6 unittest tests, 2 task artifacts, 11 required repo files, 3 schemas, and public voltage evaluator smoke.

## v0 implementation — N-1 contingency screening public surrogate

- Added the second executable v0 family: `contingency_screening` for N-1 branch-outage ranking and islanding detection.
- Followed TDD: first added `tests/test_contingency_screening_evaluator.py` and observed RED on missing `baselines.contingency_screening`; then implemented evaluator, baseline, task artifact, and sample submission.
- New artifacts: `prototype/evaluators/evaluate_contingency_screening.py`, `baselines/contingency_screening/baseline.py`, `tasks/contingency_screening/public/case_001/task.json`, and `sample_submission.json`.
- Task source provenance is explicit and bilingual-plan-aligned: arXiv:1904.00044v1 for fast contingency screening and arXiv:1904.03587v1 for N-1 grid-splitting/islanding detection.
- Verification: contingency evaluator smoke returns feasible score 1.0; `./scripts/check.sh` passes with 10 unittest tests and 3 validated task artifacts.

## v0 implementation — overcurrent protection deterministic evaluator

- Added the third executable v0 family: `overcurrent_protection` for deterministic line overcurrent relay pickup/time-delay setting.
- Followed TDD: first added `tests/test_overcurrent_protection_evaluator.py` and observed RED on missing `baselines.overcurrent_protection`; then implemented evaluator, baseline, task artifact, and sample submission.
- New artifacts: `prototype/evaluators/evaluate_overcurrent_protection.py`, `baselines/overcurrent_protection/baseline.py`, `tasks/overcurrent_protection/public/case_001/task.json`, and `sample_submission.json`.
- Evaluator checks load-margin pickup, minimum-fault sensitivity, downstream selectivity time margin, CT secondary pickup range, and time-delay bounds.
- Task source provenance is explicit: `РЕЛЕЙНАЯ ЗАЩИТА В ЗАДАЧАХ С РЕШЕНИЯМИ И ПРИМЕРАМИ` lines 548–558 plus `Релейная защита. Томск` lines 5915–5917, 6594–6597, 6802–6804, and bilingual v0 slice REL-TASK-036.
- Verification: overcurrent evaluator smoke returns feasible score 1.0; `./scripts/check.sh` passes with 15 unittest tests and 4 validated task artifacts.

## v0 implementation — PV Volt-VAR deterministic public surrogate

- Added the fourth executable v0 family: `pv_volt_var` for PV inverter Volt-VAR curve control over a short distribution-feeder time series.
- Followed TDD: first added `tests/test_pv_volt_var_evaluator.py` and observed RED on missing `baselines.pv_volt_var`; then implemented evaluator, baseline, task artifact, and sample submission.
- New artifacts: `prototype/evaluators/evaluate_pv_volt_var.py`, `baselines/pv_volt_var/baseline.py`, `tasks/pv_volt_var/public/case_001/task.json`, and `sample_submission.json`.
- Evaluator checks strictly increasing voltage breakpoints, monotonic non-increasing reactive-power fraction, inverter Q capability from kVA/kW headroom, voltage-limit clearance, control effort, and per-timestep corrected voltages.
- Task source provenance is explicit: arXiv:1006.0160v1 `Local Control of Reactive Power by Distributed Photovoltaic Generators`, arXiv:1008.0878v1 `Options for Control of Reactive Power by Distributed Photovoltaic Generators`, and bilingual v0 slice GAP-TASK-009.
- Verification: PV Volt-VAR evaluator smoke returns feasible score 0.968; `./scripts/check.sh` includes smoke commands for all four executable evaluators and passes with 19 unittest tests and 5 validated task artifacts.

## v0 implementation — FLISR restoration graph surrogate

- Added the fifth executable v0 family: `flisr_restoration` for distribution feeder fault isolation and service restoration switching.
- Followed TDD: first added `tests/test_flisr_restoration_evaluator.py` and observed RED on missing `baselines.flisr_restoration`; then implemented evaluator, baseline, task artifact, and sample submission.
- New artifacts: `prototype/evaluators/evaluate_flisr_restoration.py`, `baselines/flisr_restoration/baseline.py`, `tasks/flisr_restoration/public/case_001/task.json`, and `sample_submission.json`.
- Evaluator checks that faulted branches remain open, the energized network is radial, restored load is source-reachable, priority-restored minimum is met, and switch count is penalized.
- Task source provenance is explicit: arXiv:2004.07921v1 `A Two-Stage Service Restoration Method for Electric Power Distribution Systems` and bilingual v0 slice GAP-TASK-003.
- Verification: FLISR evaluator smoke returns feasible score 0.96 with restored_load_kw 170.0 and priority_restored 10.0; `./scripts/check.sh` includes smoke commands for all five executable evaluators and passes with 23 unittest tests and 6 validated task artifacts.

## v0 implementation — FDI state-estimation detection surrogate

- Added the sixth executable v0 family: `fdi_state_estimation` for false-data injection detection and corrected DC state-estimate accuracy.
- Followed TDD: first added `tests/test_fdi_state_estimation_evaluator.py` and observed RED on missing `baselines.fdi_state_estimation`; then implemented evaluator, residual-threshold baseline, task artifact, and sample submission.
- New artifacts: `prototype/evaluators/evaluate_fdi_state_estimation.py`, `baselines/fdi_state_estimation/baseline.py`, `tasks/fdi_state_estimation/public/case_001/task.json`, and `sample_submission.json`.
- Evaluator checks attack-label precision/recall/F1, missed attacks, false alarms, required corrected-state variables, numeric values, and maximum corrected-state error.
- Task source provenance is explicit: arXiv:1605.06180v1, arXiv:1304.4151v4, and bilingual v0 slice GAP-TASK-006.
- Verification: FDI evaluator smoke returns feasible score 1.0, precision/recall/F1 all 1.0, and max_state_error 0.0.

## v0 implementation — FRT/grid-code compliance trace checker

- Added the seventh executable v0 family: `frt_compliance` for inverter-based resource fault ride-through and reactive-current support checks.
- Followed TDD: first added `tests/test_frt_compliance_evaluator.py` and observed RED on missing `baselines.frt_compliance`; then implemented evaluator, static envelope baseline, task artifact, and sample submission.
- New artifacts: `prototype/evaluators/evaluate_frt_compliance.py`, `baselines/frt_compliance/baseline.py`, `tasks/frt_compliance/public/case_001/task.json`, and `sample_submission.json`.
- Evaluator checks voltage/time ride-through envelope, disconnection inside the envelope, reactive-current support after a deadline, minimum voltage, event duration, and compliance declaration consistency.
- Task source provenance is explicit: arXiv:2303.00391v2, arXiv:2207.11700v3, and bilingual v0 slice GAP-TASK-011.
- Verification: FRT evaluator smoke returns feasible score 1.0, ride_through_pass true, reactive_current_pass true, min_voltage_pu 0.55; `./scripts/check.sh` now smokes all seven executable evaluators and passes with 31 unittest tests and 8 validated task artifacts.

## Agent-agnostic public smoke harness

- Added a reproducible runner layer so the executable public cases can be tried with arbitrary agents rather than only hand-run sample submissions.
- New scripts: `scripts/evaluate_submission.py` for family-based evaluator dispatch, `scripts/run_public_baselines.py` for deterministic baseline sanity, `scripts/prepare_agent_tasks.py` for portable per-case packets, and `scripts/run_agent_command.py` for command-template agents using environment variables rather than Codex/OpenCode-specific assumptions.
- New tests: `tests/test_agent_harness.py` verifies executable-case discovery, evaluator dispatch, baseline output/results writing, portable packet generation without agent lock-in, and a fake command-agent run over all seven cases.
- New docs: `docs/agent_protocol.md` and `runs/README.md` define the cross-agent packet contract, environment variables, Codex/OpenCode examples, and run artifact layout.
- `scripts/check.sh` now also exercises `run_public_baselines.py` and `prepare_agent_tasks.py` in a temporary directory.
- Verification: `./scripts/check.sh` passes with 36 unittest tests, 8 validated task artifacts, all seven evaluator smokes, public baseline summary `case_count=7`, `feasible_count=7`, `mean_score≈0.983762`, and prepared agent packets for 7 public cases.

## First public agent smoke runs

- Ran three previously discussed agent surfaces through the common packet contract: Codex CLI, OpenCode CLI, and Hermes CLI/file-toolset.
- Artifacts are under `runs/public_agent_smoke/`; summary report is `runs/public_agent_smoke/REPORT.md`.
- Historical 0–100 run, before normalized-score migration: Codex CLI `0/7` feasible; root cause was not task quality but CLI auth failure (`401 Unauthorized`, expired/reused refresh token), so no submissions were written.
- Historical 0–100 run, before normalized-score migration: OpenCode (`opencode/deepseek-v4-flash-free`) `6/7` feasible; only failed `pv_volt_var` due voltage limit violations at `t_low` and `t_high`.
- Historical 0–100 run, before normalized-score migration: Hermes CLI (`--toolsets file`) `7/7` feasible.
- Command templates used for these smoke runs are captured in `scripts/local_agent_run_commands.sh`.

## Hidden normalized agent smoke runs

- Re-ran Hermes CLI/file-toolset and OpenCode on the harder hidden `case_101` packets after migrating evaluators to normalized per-case `score ∈ [0,1]` and aggregate `mean_score`.
- Artifacts are under `runs/hidden_agent_smoke/`; summary report is `runs/hidden_agent_smoke/REPORT.md`.
- Hermes CLI (`--toolsets file`): `3/3` feasible, `mean_score=0.864412`.
- OpenCode (`opencode/deepseek-v4-flash-free`): `2/3` feasible, `mean_score=0.541778`; produced a submission for every case but failed hidden `pv_volt_var` due voltage-limit violations at `t_deep_low`, `t_shallow_high`, and `t_deep_high`.
- Shared feasible results: both agents passed `contingency_screening` with `score=0.8` and `pf_voltage_repair` with `score=0.825333`.
- Verification: `./scripts/check.sh` passes with 41 unittest tests, 11 validated task artifacts, all seven evaluator smokes, public baseline `mean_score=0.983762`, and prepared public agent packets.

## Full 41-task balanced-core packaging

- Promoted the v4 balanced-core shortlist from 7 executable MVP families to 41 public executable tasks.
- Added/updated public task artifacts so each candidate has `task.json`, `sample_submission.json`, registered evaluator dispatch, and public baseline support.
- Added a generic deterministic expected-answer evaluator for the newly packaged literature-derived candidates while preserving the seven domain-specific surrogate evaluators already present.
- Added required bilingual task presentation under `bilingual.title`, `bilingual.objective`, and `bilingual.instructions`, each with `en` and `ru` text.
- New inventory: `docs/bilingual_task_inventory.md` lists all 41 tasks in English and Russian.
- Regenerated `runs/agent_packets/public_v0/` and `runs/public_baselines/latest/` for 41 public cases.
- Verification: `./scripts/check.sh` passes with 42 unittest tests, 44 validated task artifacts, one-by-one evaluation of all 41 public sample submissions, public baseline `case_count=41`, `feasible_count=41`, `mean_score=0.997228`, and prepared public agent packets for all 41 cases.
