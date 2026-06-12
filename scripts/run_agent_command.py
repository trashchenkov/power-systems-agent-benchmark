"""Run an arbitrary command-line agent on prepared benchmark task packets."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import sys
import time
from pathlib import Path
from typing import Any

ROOT_FOR_IMPORTS = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORTS) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORTS))

from scripts.evaluate_submission import evaluate_submission_file, result_row


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_agent_command(
    root: Path,
    packets_dir: Path,
    out_dir: Path,
    agent_name: str,
    command: str,
    timeout_s: int = 300,
) -> dict[str, Any]:
    """Run a shell command once per packet and evaluate produced submissions.

    The command is intentionally agent-agnostic. It runs inside a per-case
    sandbox copy of the packet (cwd = sandbox) and receives environment
    variables: BENCH_AGENT, BENCH_FAMILY, BENCH_SPLIT, BENCH_CASE_ID,
    BENCH_TASK_ID, BENCH_PACKET_DIR, BENCH_TASK_PATH,
    BENCH_INSTRUCTIONS_PATH, BENCH_SUBMISSION_PATH. BENCH_ROOT is deliberately
    not exposed.
    """
    manifest = _load_json(packets_dir / "manifest.json")
    submissions_dir = out_dir / "submissions"
    logs_dir = out_dir / "logs"
    submissions_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    rows = []

    for packet in manifest.get("packets", []):
        family = packet["family"]
        split = packet.get("split", "public")
        case_id = packet["case_id"]
        packet_name = f"{family}__{split}__{case_id}"
        packet_dir = Path(packet["packet_dir"])
        source_task_path = root / "tasks" / family / split / case_id / "task.json"
        final_submission = submissions_dir / f"{packet_name}.json"
        # Isolation: the agent works on a copy of the packet in a temp dir
        # OUTSIDE the repository, with the sandbox as cwd and no BENCH_ROOT /
        # repo PYTHONPATH. A repo-relative path can no longer reach evaluator
        # or baseline code (one agent previously self-evaluated against the
        # leaked oracle). This is relocation, not a jail: adversarial agents
        # need containers on the evaluation host.
        sandbox = Path(tempfile.mkdtemp(prefix=f"bench_{packet_name}_"))
        for item in packet_dir.iterdir():
            if item.is_file():
                shutil.copyfile(item, sandbox / item.name)
        sandbox_submission = sandbox / "submission.json"
        env = os.environ.copy()
        env.pop("BENCH_ROOT", None)
        env.update(
            {
                "BENCH_AGENT": agent_name,
                "BENCH_FAMILY": family,
                "BENCH_SPLIT": split,
                "BENCH_CASE_ID": case_id,
                "BENCH_TASK_ID": str(packet.get("task_id", "")),
                "BENCH_PACKET_DIR": str(sandbox),
                "BENCH_TASK_PATH": str(sandbox / "task.json"),
                "BENCH_INSTRUCTIONS_PATH": str(sandbox / "instructions.md"),
                "BENCH_SUBMISSION_PATH": str(sandbox_submission),
            }
        )
        started = time.time()
        try:
            completed = subprocess.run(
                command,
                shell=True,
                cwd=sandbox,
                env=env,
                text=True,
                capture_output=True,
                stdin=subprocess.DEVNULL,
                timeout=timeout_s,
                check=False,
            )
            stdout = completed.stdout
            stderr = completed.stderr
            returncode = completed.returncode
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", errors="replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", errors="replace")
            stderr = stderr + f"\nTIMEOUT: command exceeded {timeout_s} seconds\n"
            returncode = 124
        elapsed_s = round(time.time() - started, 6)
        (logs_dir / f"{packet_name}.stdout.txt").write_text(stdout, encoding="utf-8")
        (logs_dir / f"{packet_name}.stderr.txt").write_text(stderr, encoding="utf-8")
        if not sandbox_submission.exists():
            row = {
                "agent": agent_name,
                "family": family,
                "split": split,
                "case_id": case_id,
                "task_id": packet.get("task_id"),
                "returncode": returncode,
                "elapsed_s": elapsed_s,
                "result": {
                    "feasible": False,
                    "score": 0.0,
                    "violations": ["agent did not write submission.json"],
                },
            }
        else:
            shutil.copyfile(sandbox_submission, final_submission)
            try:
                result = evaluate_submission_file(source_task_path, final_submission)
            except Exception as exc:  # an evaluator crash must not kill the run
                result = {
                    "feasible": False,
                    "score": 0.0,
                    "violations": [f"evaluator exception: {type(exc).__name__}: {exc}"],
                    "evaluator_exception": True,
                }
            row = result_row(source_task_path, final_submission, result)
            row.update({"agent": agent_name, "returncode": returncode, "elapsed_s": elapsed_s})
        rows.append(row)
        shutil.rmtree(sandbox, ignore_errors=True)

    results_path = out_dir / "results.jsonl"
    with results_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    summary = {
        "agent": agent_name,
        "command": command,
        "case_count": len(rows),
        "feasible_count": sum(1 for row in rows if row["result"].get("feasible")),
        "mean_score": round(
            sum(float(row["result"].get("score", 0.0)) for row in rows) / len(rows), 6
        )
        if rows
        else 0.0,
        "results_path": str(results_path),
        "submissions_dir": str(submissions_dir),
        "logs_dir": str(logs_dir),
    }
    _write_json(out_dir / "summary.json", summary)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run an arbitrary command-line agent over prepared task packets.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Benchmark repository root")
    parser.add_argument("--packets", type=Path, required=True, help="Directory created by scripts/prepare_agent_tasks.py")
    parser.add_argument("--out", type=Path, required=True, help="Output run directory")
    parser.add_argument("--agent-name", required=True, help="Human-readable agent name")
    parser.add_argument("--command", required=True, help="Shell command to run once per packet")
    parser.add_argument("--timeout-s", type=int, default=300, help="Per-case timeout")
    args = parser.parse_args(argv)
    summary = run_agent_command(args.root, args.packets, args.out, args.agent_name, args.command, args.timeout_s)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["feasible_count"] == summary["case_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
