"""Run an arbitrary command-line agent on prepared benchmark task packets."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
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


TRANSIENT_PATTERNS = (
    "remoteexception",
    "servererror",
    "readtimeout",
    "remoteprotocolerror",
    "http/1.1 5",
    "http 5",
    "error 5",
    " 429",
    "too many requests",
    "rate limit",
    "connection reset",
    "connection refused",
    "spend limit",
    "usage limit",
    "quota exceeded",
    "insufficient credit",
    "billing",
)
RETRYABLE_CLASSES = {"provider_transient", "early_transport_abort"}
PACKET_FILES = ("task.json", "instructions.md")
EARLY_ABORT_S = 30.0


def _kill_process_group(proc: subprocess.Popen) -> None:
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def classify_failure(returncode: int, stdout: str, stderr: str, elapsed_s: float, timeout_s: int) -> str:
    """Classify a no-submission attempt.

    provider_transient / early_transport_abort are infrastructure failures and
    may be retried; timeout_budget (the agent used the whole per-case budget)
    and agent_no_submission (the agent ran but broke the file contract) are
    agent failures and are never retried automatically.
    """
    if returncode == 124:
        return "timeout_budget"
    text = ((stdout or "") + "\n" + (stderr or "")).lower()
    if any(pattern in text for pattern in TRANSIENT_PATTERNS):
        return "provider_transient"
    if returncode != 0 and elapsed_s < EARLY_ABORT_S and not (stdout or "").strip():
        return "early_transport_abort"
    return "agent_no_submission"


def run_agent_command(
    root: Path,
    packets_dir: Path,
    out_dir: Path,
    agent_name: str,
    command: str,
    timeout_s: int = 300,
    max_attempts: int = 1,
    retry_backoff_s: float = 30.0,
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

        # Retry policy: only infrastructure-transient failures (provider/transport)
        # are retried, never quality failures, contract violations, or budget
        # timeouts — retrying those would silently turn the benchmark into
        # best-of-N. Every attempt's logs are preserved.
        attempts: list[dict[str, Any]] = []
        selected_attempt = None
        for attempt in range(1, max(1, max_attempts) + 1):
            # Isolation: the agent works on a fresh copy of the packet in a
            # temp dir OUTSIDE the repository, with the sandbox as cwd and no
            # BENCH_ROOT / repo PYTHONPATH. A repo-relative path can no longer
            # reach evaluator or baseline code (one agent previously
            # self-evaluated against the leaked oracle). This is relocation,
            # not a jail: adversarial agents need containers.
            sandbox = Path(tempfile.mkdtemp(prefix=f"bench_{packet_name}_a{attempt}_"))
            # Copy only the packet's protocol files. A stray submission.json that an
            # agent wrote into the source packet (e.g. via the absolute path in
            # instructions.md) must never reach a later attempt or run.
            for name in PACKET_FILES:
                if (packet_dir / name).is_file():
                    shutil.copyfile(packet_dir / name, sandbox / name)
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
            # The agent runs in its own process group so that a budget timeout
            # terminates the whole agent, not only the shell wrapper; surviving
            # agents would otherwise keep consuming the host's resources.
            proc = subprocess.Popen(
                command,
                shell=True,
                cwd=sandbox,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
            )
            try:
                stdout, stderr = proc.communicate(timeout=timeout_s)
                returncode = proc.returncode
            except subprocess.TimeoutExpired:
                _kill_process_group(proc)
                stdout, stderr = proc.communicate()
                stderr = (stderr or "") + f"\nTIMEOUT: command exceeded {timeout_s} seconds\n"
                returncode = 124
            finally:
                # Background children of an agent that exited normally are cleaned up too.
                _kill_process_group(proc)
            elapsed_s = round(time.time() - started, 6)
            suffix = f".attempt{attempt}" if max_attempts > 1 else ""
            (logs_dir / f"{packet_name}{suffix}.stdout.txt").write_text(stdout, encoding="utf-8")
            (logs_dir / f"{packet_name}{suffix}.stderr.txt").write_text(stderr, encoding="utf-8")
            has_submission = sandbox_submission.exists()
            failure_class = None if has_submission else classify_failure(returncode, stdout, stderr, elapsed_s, timeout_s)
            attempts.append(
                {
                    "attempt": attempt,
                    "returncode": returncode,
                    "elapsed_s": elapsed_s,
                    "failure_class": failure_class,
                }
            )
            if has_submission:
                shutil.copyfile(sandbox_submission, final_submission)
                selected_attempt = attempt
                shutil.rmtree(sandbox, ignore_errors=True)
                break
            shutil.rmtree(sandbox, ignore_errors=True)
            if failure_class not in RETRYABLE_CLASSES or attempt >= max_attempts:
                break
            time.sleep(retry_backoff_s)

        last = attempts[-1]
        if selected_attempt is None:
            final_class = last["failure_class"]
            violations = [f"agent did not write submission.json ({final_class})"]
            result = {"feasible": False, "score": 0.0, "violations": violations}
            if final_class in RETRYABLE_CLASSES:
                result["infra_unresolved"] = True
            row = {
                "agent": agent_name,
                "family": family,
                "split": split,
                "case_id": case_id,
                "task_id": packet.get("task_id"),
                "returncode": last["returncode"],
                "elapsed_s": last["elapsed_s"],
                "result": result,
            }
        else:
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
            row.update({"agent": agent_name, "returncode": last["returncode"], "elapsed_s": last["elapsed_s"]})
        retried = len(attempts) > 1
        first_ok = selected_attempt == 1
        row.update(
            {
                "attempt_count": len(attempts),
                "retried": retried,
                "selected_attempt": selected_attempt,
                "failure_class_initial": attempts[0]["failure_class"],
                "failure_class_final": last["failure_class"] if selected_attempt is None else None,
                "raw_first_attempt": row["result"] if first_ok else {
                    "feasible": False,
                    "score": 0.0,
                    "failure_class": attempts[0]["failure_class"],
                },
            }
        )
        rows.append(row)
        # Progress log: rows survive an interrupted run (results.jsonl is written at the end).
        with (out_dir / "results.partial.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    results_path = out_dir / "results.jsonl"
    with results_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    raw_results = [row.get("raw_first_attempt", row["result"]) for row in rows]
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
        "raw_feasible_count": sum(1 for r in raw_results if r.get("feasible")),
        "raw_mean_score": round(
            sum(float(r.get("score", 0.0)) for r in raw_results) / len(raw_results), 6
        )
        if raw_results
        else 0.0,
        "max_attempts": max_attempts,
        "retried_count": sum(1 for row in rows if row.get("retried")),
        "recovered_count": sum(
            1 for row in rows if row.get("retried") and row.get("selected_attempt") is not None
        ),
        "infra_unresolved_count": sum(
            1 for row in rows if row["result"].get("infra_unresolved")
        ),
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
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=1,
        help="Attempts per case; >1 enables retries for transient infrastructure failures only",
    )
    parser.add_argument(
        "--retry-backoff-s",
        type=float,
        default=30.0,
        help="Pause before a transient-failure retry",
    )
    args = parser.parse_args(argv)
    summary = run_agent_command(
        args.root,
        args.packets,
        args.out,
        args.agent_name,
        args.command,
        args.timeout_s,
        max_attempts=args.max_attempts,
        retry_backoff_s=args.retry_backoff_s,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["feasible_count"] == summary["case_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
