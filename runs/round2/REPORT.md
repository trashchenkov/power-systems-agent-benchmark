# Repeated-run evaluation (round 2, 2026-10)

Repeated runs that replace the single-run reference round (`runs/canonical_round1/`)
and the single-run model-harness grid (`runs/extra_models/`) as the results reported
in the paper. Each configuration was run several times on the same instances, so the
tables report means and run-to-run standard deviations instead of single draws.

## Protocol

- Harness and evaluator code of this release; `scripts/run_repeated_agent.py` runs `k`
  independent repeats of the standard runner (`scripts/run_agent_command.py`) and
  `scripts/summarize_repeats.py` computes the statistics.
- Per-case budget 600 s, `--max-attempts 2` (retry only transient provider/transport
  failures). No case needed a retry or a manual rerun.
- Every case runs in a fresh temporary sandbox with fresh agent state (no memories or
  session database shared between cases), and every repeat uses its own pristine copy
  of the task packets.
- Agent commands: `agent_commands.sh` (prompts identical to round 1). Agents are used
  as shipped; sampling settings are harness defaults.

| configuration | harness version | model route | split(s) | k |
|---|---|---|---|---|
| Codex + gpt-5.5 (medium) | codex-cli 0.139.0 | OpenRouter-compatible gateway, `openai/gpt-5.5` (Responses API) | 41 public + 41 held-out | 5 |
| Cursor + composer-2.5 | cursor-agent 2026.06.12-01-15-52-7244546 | native Cursor service | 41 public + 41 held-out | 5 |
| OpenCode + deepseek-v4-flash | opencode 1.15.13 | OpenRouter-compatible gateway, `deepseek/deepseek-v4-flash` | 41 public + 41 held-out | 5 |
| OpenCode / Aider + Kimi K2.5, GLM-4.6, Claude Haiku 4.5 | opencode 1.15.13 / aider 0.86.2 | OpenRouter-compatible gateway | 41 public | 3 |
| OpenCode / Aider + Qwen3-Coder-Next | opencode 1.15.13 / aider 0.86.2 | OpenRouter (provider Parasail, bf16) | 41 public | 3 |

The gateway proxy used for streaming access is `tagme_stream_proxy.py` (credentials are
read from a local file and never logged). The held-out instances (`case_501`) come from
`scripts/generate_hidden_cases.py` with a private seed that is not published.

## Main round (Table II of the paper)

Feasible and perfect counts are means over the five runs.

| configuration | split | feasible | perfect | mean ± SD | pass@1 | pass^5 |
|---|---|---:|---:|---:|---:|---:|
| Codex + gpt-5.5 | public | 39.8 | 38.4 | 0.968 ± 0.011 | 0.937 | 0.902 |
| | held-out | 40.0 | 38.2 | 0.972 ± 0.000 | 0.932 | 0.927 |
| Cursor + composer-2.5 | public | 40.8 | 40.2 | 0.995 ± 0.011 | 0.980 | 0.951 |
| | held-out | 39.8 | 38.6 | 0.969 ± 0.021 | 0.941 | 0.878 |
| OpenCode + deepseek-v4-flash | public | 36.0 | 34.8 | 0.878 ± 0.039 | 0.849 | 0.683 |
| | held-out | 37.0 | 36.2 | 0.902 ± 0.048 | 0.883 | 0.659 |

pass@1 is the expected fraction of instances solved perfectly by one run; pass^5 is the
fraction solved perfectly in all five runs. Scores were identical across all five runs
on 79 (Codex), 75 (Cursor), and 57 (OpenCode) of the 82 instances.

## Model-harness grid (Table III of the paper)

Public split, mean ± SD over three runs.

| model | OpenCode | Aider |
|---|---:|---:|
| Kimi K2.5 | 0.870 ± 0.014 | 0.723 ± 0.051 |
| GLM-4.6 | 0.860 ± 0.027 | 0.690 ± 0.027 |
| Claude Haiku 4.5 | 0.821 ± 0.051 | 0.546 ± 0.041 |
| Qwen3-Coder-Next | 0.592 ± 0.060 | 0.550 ± 0.037 |

167 of Aider's 182 infeasible submissions were well-formed answers that failed
engineering checks. OpenCode with Qwen3-Coder-Next left 18 of 123 cases without a
submission (all missing submissions count as zero).

## Files

- `<run>/rep_<r>/summary.json` — per-repeat summary; held-out results only as aggregates.
- `<run>/rep_<r>/results_public.jsonl`, `submissions/`, `logs/` — public per-case
  artifacts (logs sanitized: local paths replaced by placeholders).
- `<run>/repeat_summary.json` — run-level statistics and the public per-case table.
- `t2_analysis.json`, `t3_analysis.json` — the numbers in the tables above.
- `RUNLOG.md` — operator log of the round, including the runs that were discarded.

## Discarded runs and fixes made during the round

All discarded runs were excluded as a whole, independently of their scores.

1. **Shared packet directory.** `instructions.md` names the packet's own absolute
   `submission.json` path, while the agent works in a sandbox copy. Some agents wrote
   to that absolute path; with all repeats reading one shared packet directory, such a
   file was copied into later sandboxes of the same task. The first attempt of the
   round was discarded. Fix: the runner copies only `task.json` and `instructions.md`
   into a sandbox, each repeat gets its own packet copy, and files written into a
   packet are reported as `files_written_into_packets` (they are never scored).
2. **Orphaned agents after timeouts.** The runner killed only the shell wrapper on a
   budget timeout. When the gateway returned HTTP 503 for every Qwen3-Coder-Next
   request, the hanging agents accumulated and exhausted the host's memory. The Qwen
   cells were discarded and rerun through OpenRouter; the runner now kills the agent's
   whole process group (`tests/test_runner_timeout.py`).

## Known protocol issue

The absolute path in `instructions.md` and the "write to the current directory" prompt
disagree. It is left unchanged in this round so that the conditions match round 1; an
agent that writes only to the absolute path receives no score for that case. Most of
OpenCode's missing submissions above have this cause.
