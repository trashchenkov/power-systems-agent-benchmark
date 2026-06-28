# Power Systems Agent Benchmark

[![arXiv](https://img.shields.io/badge/arXiv-2606.20950-b31b1b.svg)](https://arxiv.org/abs/2606.20950)
[![DOI](https://zenodo.org/badge/1265507049.svg)](https://doi.org/10.5281/zenodo.20753045)

Executable benchmark prototype for tool-using AI agents in electric power systems.

This project is intentionally not a text QA benchmark. Agents submit structured actions or decisions; task evaluators recompute physical, operational, protection, reliability, or compliance outcomes and score the result programmatically.

## Current status

Runnable v0 prototype:

- benchmark design: `benchmark_spec_v0.md`
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
- executable public task families: the full **41-family balanced core** (catalog in
  `docs/bilingual_task_inventory.md`)
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
runs/
  canonical_round1/                  # curated aggregate reference summaries
  extra_models/                      # curated aggregate model-harness summaries
  generator_validation/              # hidden-generator validation summary
```

## Hidden case generation

Hidden cases are intentionally untracked (`.gitignore`: `**/hidden/`). Instead of
shipping them, the repository ships a deterministic generator with a registered
perturbation for every public family. The evaluation host derives hidden cases
from a private seed; every generated case is accepted only if the family
baseline solves it and the evaluator marks the solution feasible:

```bash
python scripts/generate_hidden_cases.py --seed <private-seed> --case-id 201
```

Anyone with the repository can audit how hidden cases are produced, but without
the seed the concrete hidden numbers stay unknown. Keep leaderboard seeds off
the public record.

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

## Retry policy for agent runs

`run_agent_command.py` defaults to a single attempt per case (raw protocol).
With `--max-attempts 2..3` it retries **only transient infrastructure
failures** — provider/transport signatures (RemoteException, ServerError,
ReadTimeout, RemoteProtocolError, HTTP 5xx/429, rate limits) and early silent
transport aborts. Quality failures, contract violations (submission not
written by a healthy agent), and per-case budget timeouts are never retried:
that would silently turn the benchmark into best-of-N. All attempt logs are
preserved (`*.attemptN.stdout.txt`), every result row records
`attempt_count` / `failure_class_initial` / `selected_attempt` /
`raw_first_attempt`, and the summary reports both raw
(`raw_feasible_count`, `raw_mean_score`) and retry-normalized
(`feasible_count`, `mean_score`) metrics plus `infra_unresolved_count`, so
provider reliability never masquerades as agent capability.

## Reference evaluation

The canonical reference round — three command-line agents, one public and one freshly
generated held-out case per family, optimum-normalized scoring — is summarized in
`runs/canonical_round1/REPORT.md`:

| agent (model) | public mean | held-out mean |
|---|---|---|
| codex (gpt-5.5 medium) | 0.973 | 0.995 |
| cursor (composer-2.5) | 0.973 | 1.000 |
| opencode (deepseek-v4-flash-free) | 0.951 | 0.973 |

Per the leak policy, only aggregate per-agent summaries are published for the held-out
split; per-case held-out submissions, results, and logs are not.

## Public executable task inventory

The public benchmark covers a full **41-task balanced core**. Every public task is packaged as `tasks/<family>/public/case_001/task.json` plus `sample_submission.json`, has a registered evaluator, and includes English and Russian presentation fields under `bilingual`.

Inventory / реестр: `docs/bilingual_task_inventory.md`.


## Citation

If you use this benchmark or its experiment artifacts, cite the archived software
release. The version DOI for the paper artifact release is
[`10.5281/zenodo.20753046`](https://doi.org/10.5281/zenodo.20753046); the DOI badge
above resolves through the Zenodo concept DOI for the repository.

```bibtex
@software{trashchenkov_power_systems_agent_benchmark_2026,
  author = {Trashchenkov, Sergei},
  title = {Power Systems Agent Benchmark: Executable Evaluation of AI Agents in Electric Power Engineering},
  year = {2026},
  version = {v0.1-paper-artifacts},
  doi = {10.5281/zenodo.20753046},
  url = {https://github.com/trashchenkov/power-systems-agent-benchmark}
}
```

## Next steps beyond this MVP slice

1. Replace selected deterministic surrogates with simulator-backed evaluators (`pandapower`, OpenDSS, or DC-SE where appropriate).
2. Expand hidden cases across the 41 public executable tasks.
3. Add pinned dependencies and CI for simulator-backed tracks.
4. Automate agent-matrix report generation while keeping task failure, harness failure, model/provider failure, and auth failure separate.
