#!/usr/bin/env bash
# Local command templates for smoke-running agent CLIs through scripts/run_agent_command.py.
# Source this file from the benchmark repo root or copy the command strings manually.

CODEX_AGENT_COMMAND='codex exec --skip-git-repo-check --sandbox workspace-write --cd "$BENCH_PACKET_DIR" "Read instructions.md and task.json. Solve the executable benchmark task. Write valid JSON exactly to submission.json in the current directory. Do not modify other files. Do not output Markdown."'

OPENCODE_AGENT_COMMAND='opencode run --model opencode/deepseek-v4-flash-free --dir "$BENCH_PACKET_DIR" "Read instructions.md and task.json. Solve the executable benchmark task. Write only submission.json as valid JSON. Do not modify other files."'

HERMES_AGENT_COMMAND='hermes chat -Q --toolsets file -q "Read $BENCH_INSTRUCTIONS_PATH and $BENCH_TASK_PATH. Solve the executable benchmark task. Write valid JSON exactly to $BENCH_SUBMISSION_PATH. Do not modify other files."'
