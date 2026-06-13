"""Retry policy: transient infrastructure failures may be retried, quality
failures and budget timeouts never are, and both raw and retry-normalized
metrics are reported."""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.prepare_agent_tasks import prepare_agent_tasks
from scripts.run_agent_command import classify_failure, run_agent_command

ROOT = Path(__file__).resolve().parents[1]


def _one_packet_dir(tmp: Path) -> Path:
    packets = tmp / "packets_all"
    prepare_agent_tasks(ROOT, packets)
    manifest = json.loads((packets / "manifest.json").read_text(encoding="utf-8"))
    keep = [p for p in manifest["packets"] if p["family"] == "ybus_construction"]
    single = tmp / "packets_one"
    single.mkdir()
    for p in keep:
        shutil.copytree(Path(p["packet_dir"]), single / Path(p["packet_dir"]).name)
        for key in ("packet_dir", "task_path"):
            if key in p:
                p[key] = p[key].replace(str(packets), str(single))
    manifest["packets"] = keep
    manifest["case_count"] = len(keep)
    (single / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return single


def _flaky_command(marker: Path) -> str:
    """Fails once with a transient provider signature, then solves via baseline."""
    return (
        f"if [ ! -f {marker} ]; then touch {marker}; "
        "echo 'httpx.ReadTimeout: timed out' >&2; exit 1; fi; "
        f"PYTHONPATH={ROOT} {sys.executable} -c \""
        "import json, os; from pathlib import Path; "
        "from scripts.run_public_baselines import solve_with_baseline; "
        f"task=json.loads((Path('{ROOT}')/'tasks'/os.environ['BENCH_FAMILY']/os.environ['BENCH_SPLIT']/os.environ['BENCH_CASE_ID']/'task.json').read_text()); "
        "submission=solve_with_baseline(os.environ['BENCH_FAMILY'], task); "
        "Path(os.environ['BENCH_SUBMISSION_PATH']).write_text(json.dumps(submission))\""
    )


class ClassifyFailureTests(unittest.TestCase):
    def test_provider_signatures_are_transient(self):
        for sig in ("RemoteException", "ServerError: boom", "httpx.ReadTimeout", "RemoteProtocolError", "HTTP 503", "rate limit exceeded", "You've hit your monthly spend limit", "quota exceeded"):
            self.assertEqual(classify_failure(1, "", sig, 5.0, 600), "provider_transient", sig)

    def test_budget_timeout_is_not_retryable(self):
        self.assertEqual(classify_failure(124, "long reasoning...", "", 600.0, 600), "timeout_budget")

    def test_early_silent_abort_is_transient(self):
        self.assertEqual(classify_failure(1, "", "", 2.0, 600), "early_transport_abort")

    def test_agent_contract_break_is_not_retryable(self):
        # Ran for a while, produced output, no transient signature, no file.
        self.assertEqual(classify_failure(0, "I solved it and printed JSON here", "", 120.0, 600), "agent_no_submission")


class RetryPolicyTests(unittest.TestCase):
    def test_transient_failure_recovers_and_both_metrics_reported(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            packets = _one_packet_dir(tmp)
            marker = tmp / "failed_once.marker"
            summary = run_agent_command(
                ROOT, packets, tmp / "run", "flaky-agent", _flaky_command(marker),
                timeout_s=120, max_attempts=2, retry_backoff_s=0.0,
            )
            self.assertEqual(summary["case_count"], 1)
            self.assertEqual(summary["feasible_count"], 1)
            self.assertEqual(summary["raw_feasible_count"], 0)
            self.assertEqual(summary["retried_count"], 1)
            self.assertEqual(summary["recovered_count"], 1)
            self.assertEqual(summary["infra_unresolved_count"], 0)
            row = json.loads((tmp / "run" / "results.jsonl").read_text().splitlines()[0])
            self.assertEqual(row["attempt_count"], 2)
            self.assertTrue(row["retried"])
            self.assertEqual(row["selected_attempt"], 2)
            self.assertEqual(row["failure_class_initial"], "provider_transient")
            self.assertFalse(row["raw_first_attempt"]["feasible"])
            # all attempt logs preserved
            logs = tmp / "run" / "logs"
            self.assertTrue((logs / "ybus_construction__public__case_001.attempt1.stderr.txt").exists())
            self.assertTrue((logs / "ybus_construction__public__case_001.attempt2.stdout.txt").exists())

    def test_default_single_attempt_does_not_retry(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            packets = _one_packet_dir(tmp)
            marker = tmp / "failed_once.marker"
            summary = run_agent_command(
                ROOT, packets, tmp / "run", "flaky-agent", _flaky_command(marker),
                timeout_s=120,
            )
            self.assertEqual(summary["feasible_count"], 0)
            self.assertEqual(summary["retried_count"], 0)
            self.assertEqual(summary["infra_unresolved_count"], 1)
            row = json.loads((tmp / "run" / "results.jsonl").read_text().splitlines()[0])
            self.assertEqual(row["attempt_count"], 1)
            self.assertTrue(row["result"]["infra_unresolved"])

    def test_quality_failure_is_never_retried(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            packets = _one_packet_dir(tmp)
            command = 'echo "{\\"buses\\": null, \\"ybus\\": null}" > "$BENCH_SUBMISSION_PATH"'
            summary = run_agent_command(
                ROOT, packets, tmp / "run", "bad-agent", command,
                timeout_s=60, max_attempts=3, retry_backoff_s=0.0,
            )
            self.assertEqual(summary["feasible_count"], 0)
            self.assertEqual(summary["retried_count"], 0)
            row = json.loads((tmp / "run" / "results.jsonl").read_text().splitlines()[0])
            self.assertEqual(row["attempt_count"], 1)
            self.assertFalse(row["result"]["feasible"])
            self.assertTrue(row["result"]["violations"])


if __name__ == "__main__":
    unittest.main()
