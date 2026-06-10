# Power Systems Agent Benchmark

Executable benchmark prototype for tool-using AI agents in electric power systems.

This project is intentionally not a text QA benchmark. Agents submit structured actions or decisions; task evaluators recompute physical, operational, protection, reliability, or compliance outcomes and score the result programmatically.

## Current status

Runnable v0 prototype:

- benchmark design: `benchmark_spec_v0.md`
- packaging decision: `PACKAGING_STRATEGY.md`
- bilingual executable-slice plan:
  - `literature/v0_executable_benchmark_slice.ru.md`
  - `literature/v0_executable_benchmark_slice.en.md`
  - `docs/plans/v0-executable-benchmark.ru.md`
  - `docs/plans/v0-executable-benchmark.en.md`
- docs:
  - `docs/evaluator_contract.md`
  - `docs/public_hidden_split.md`
  - `docs/metrics.md`
  - `docs/agent_protocol.md`
- schemas:
  - `schemas/task.schema.json`
  - `schemas/submission.schema.json`
  - `schemas/evaluation-result.schema.json`
- executable public task families:
  - `contingency_screening`
  - `fdi_state_estimation`
  - `flisr_restoration`
  - `frt_compliance`
  - `overcurrent_protection`
  - `pf_voltage_repair`
  - `pv_volt_var`
- agent-agnostic runner scripts:
  - `scripts/evaluate_submission.py`
  - `scripts/run_public_baselines.py`
  - `scripts/prepare_agent_tasks.py`
  - `scripts/run_agent_command.py`

The current evaluators are deterministic public surrogates. They lock the task/submission/evaluation contract before replacing selected internals with simulator-backed implementations such as `pandapower`, OpenDSS, DC state estimation, or more detailed protection models.

## Why executable evaluation

Primary score should come from hidden recomputation, not LLM-as-a-judge report grading:

1. apply the submitted actions or decisions to a case;
2. rerun simulator/formula/graph evaluator;
3. check hard constraints;
4. compute objective metrics;
5. emit machine-readable scoring evidence.

Rationale text can be stored and optionally judged as a secondary diagnostic, but it should not determine the main leaderboard.

## Repository layout

```text
benchmark_spec_v0.md                 # benchmark contract draft
PACKAGING_STRATEGY.md                # skill vs benchmark repo boundary
docs/agent_protocol.md               # CLI-agent packet protocol
schemas/task.schema.json             # common task artifact schema
scripts/validate_benchmark_artifacts.py
scripts/evaluate_submission.py
scripts/run_public_baselines.py
scripts/prepare_agent_tasks.py
scripts/run_agent_command.py
tasks/
  <family>/public/case_001/
    task.json
    sample_submission.json
prototype/
  evaluators/evaluate_<family>.py
baselines/
  <family>/baseline.py
tests/
  test_*_evaluator.py
  test_agent_harness.py
literature/
  v0_executable_benchmark_slice.*.md
  task_bank_*.md
runs/
  public_baselines/
  agent_packets/
  public_agent_smoke/
```

## Smoke check

From the repository root:

```bash
./scripts/check.sh
```

The check runs unit tests, artifact validation, evaluator smokes, one-by-one evaluation for all 41 public executable sample submissions, public baseline sanity, and agent-packet preparation.

Manual baseline run:

```bash
python scripts/run_public_baselines.py --out runs/public_baselines/latest
```

Prepare portable task packets for arbitrary CLI agents:

```bash
python scripts/prepare_agent_tasks.py --out runs/agent_packets/public_v0
```

Run a command-line agent once per packet:

```bash
python scripts/run_agent_command.py \
  --packets runs/agent_packets/public_v0 \
  --out runs/public_agent_smoke/<agent-name> \
  --agent-name <agent-name> \
  --command '<agent command that writes $BENCH_SUBMISSION_PATH>'
```

## First agent smoke results

Latest historical local report: `runs/public_agent_smoke/REPORT.md`.

- Historical 0–100 run before the normalized-score migration: Hermes CLI (`--toolsets file`) was 7/7 feasible.
- Historical 0–100 run before the normalized-score migration: OpenCode (`opencode/deepseek-v4-flash-free`) was 6/7 feasible and failed `pv_volt_var` on voltage-limit violations.
- Codex CLI: 0/7 feasible because the local Codex OAuth session failed before writing submissions (`401 Unauthorized`, expired/reused refresh token). This is an environment/auth issue, not a benchmark-mechanics failure.

## Hidden normalized smoke results

Latest hidden report: `runs/hidden_agent_smoke/REPORT.md`.

- Hermes CLI (`--toolsets file`): 3/3 feasible, `mean_score=0.864412` on hidden `case_101` packets.
- OpenCode (`opencode/deepseek-v4-flash-free`): 2/3 feasible, `mean_score=0.541778`; failed hidden `pv_volt_var` on voltage-limit violations.
- Historical run directories without the `-normalized` suffix used the old 0–100/`total_score` convention and should not be mixed with the normalized report.

## Public executable task inventory

The public benchmark now covers the full **41-task balanced core** from `literature/metadata/v4_balanced_core_shortlist.md`. Every public task is packaged as `tasks/<family>/public/case_001/task.json` plus `sample_submission.json`, has a registered evaluator, and includes English and Russian presentation fields under `bilingual`.

Inventory / реестр: `docs/bilingual_task_inventory.md`.

## Next steps beyond this MVP slice

1. Replace selected deterministic surrogates with simulator-backed evaluators (`pandapower`, OpenDSS, or DC-SE where appropriate).
2. Expand hidden cases across the 41 public executable tasks.
3. Add pinned dependencies and CI for simulator-backed tracks.
4. Automate agent-matrix report generation while keeping task failure, harness failure, model/provider failure, and auth failure separate.
