import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.prepare_agent_tasks import prepare_agent_tasks
from scripts.run_repeated_agent import main as run_repeated_main
from scripts.summarize_repeats import pass_at_k, pass_hat_k, summarize


class PassAtKTest(unittest.TestCase):
    def test_pass_at_k_estimator(self) -> None:
        self.assertEqual(pass_at_k(5, 0, 1), 0.0)
        self.assertEqual(pass_at_k(5, 5, 3), 1.0)
        self.assertAlmostEqual(pass_at_k(5, 2, 1), 0.4)
        self.assertAlmostEqual(pass_at_k(5, 2, 3), 1 - 1 / 10)
        self.assertEqual(pass_at_k(5, 3, 3), 1.0)

    def test_pass_hat_k_estimator(self) -> None:
        self.assertEqual(pass_hat_k(5, 5, 5), 1.0)
        self.assertEqual(pass_hat_k(5, 4, 5), 0.0)
        self.assertAlmostEqual(pass_hat_k(5, 4, 3), 4 / 10)

    def test_k_larger_than_repeats_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            pass_at_k(3, 1, 5)


class RepeatedRunTest(unittest.TestCase):
    def test_repeats_with_baseline_agent_are_all_perfect(self) -> None:
        family = "three_phase_short_circuit"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            prepare_agent_tasks(ROOT, tmp_path / "packets")
            command = (
                f"{sys.executable} -c \"import json, os, sys; sys.path.insert(0, {str(ROOT)!r}); "
                "from pathlib import Path; from scripts.run_public_baselines import solve_with_baseline; "
                f"task = json.loads((Path({str(ROOT)!r}) / 'tasks' / os.environ['BENCH_FAMILY'] / "
                "os.environ['BENCH_SPLIT'] / os.environ['BENCH_CASE_ID'] / 'task.json').read_text()); "
                "Path(os.environ['BENCH_SUBMISSION_PATH']).write_text(json.dumps("
                "solve_with_baseline(os.environ['BENCH_FAMILY'], task)))\""
            )
            out = tmp_path / "run"
            run_repeated_main([
                "--root", str(ROOT), "--packets", str(tmp_path / "packets"), "--out", str(out),
                "--agent-name", "baseline", "--command", command, "--families", family,
                "--repeats", "3", "--parallel", "2", "--timeout-s", "60", "--max-attempts", "1",
            ])
            manifest = json.loads((out / "packets_subset" / "manifest.json").read_text())
            self.assertEqual({p["family"] for p in manifest["packets"]}, {family})
            summary = summarize(out, [1, 3])
            self.assertEqual(summary["overall"]["repeats"], 3)
            self.assertEqual(summary["overall"]["pass@1"], 1.0)
            self.assertEqual(summary["overall"]["pass^3"], 1.0)
            self.assertEqual(summary["overall"]["sd_of_run_means"], 0.0)
            # Each repeat ran on its own packet copy whose instructions name that copy.
            for r in (1, 2, 3):
                pkt = out / f"rep_{r}" / "packets" / f"{family}__public__case_001"
                self.assertIn(str(pkt), (pkt / "instructions.md").read_text())

    def test_submission_written_into_packet_is_flagged_and_not_scored(self) -> None:
        # The agent ignores its sandbox and writes to the absolute packet path from
        # instructions.md: no submission is scored and the stray file is reported.
        family = "three_phase_short_circuit"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            prepare_agent_tasks(ROOT, tmp_path / "packets")
            agent = tmp_path / "stray_agent.py"
            agent.write_text(
                "import re\nfrom pathlib import Path\n"
                "text = Path('instructions.md').read_text()\n"
                "Path(re.search(r'`(/[^`]+submission.json)`', text).group(1)).write_text('{}')\n"
            )
            command = f'"{sys.executable}" "{agent}"'
            out = tmp_path / "run"
            run_repeated_main([
                "--root", str(ROOT), "--packets", str(tmp_path / "packets"), "--out", str(out),
                "--agent-name", "stray", "--command", command, "--families", family,
                "--repeats", "2", "--parallel", "1", "--timeout-s", "60", "--max-attempts", "1",
            ])
            for r in (1, 2):
                rep = json.loads((out / f"rep_{r}" / "summary.json").read_text())
                self.assertEqual(rep["files_written_into_packets"], [f"{family}__public__case_001/submission.json"])
                self.assertEqual(rep["feasible_count"], 0)
            self.assertFalse((tmp_path / "packets" / f"{family}__public__case_001" / "submission.json").exists())


class SandboxCopyTest(unittest.TestCase):
    def test_stray_packet_file_is_not_copied_into_sandbox(self) -> None:
        from scripts.run_agent_command import run_agent_command

        family = "three_phase_short_circuit"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            prepare_agent_tasks(ROOT, tmp_path / "packets")
            packet = tmp_path / "packets" / f"{family}__public__case_001"
            (packet / "submission.json").write_text('{"ik_max_ka": 1.0}')
            manifest = json.loads((tmp_path / "packets" / "manifest.json").read_text())
            manifest["packets"] = [p for p in manifest["packets"] if p["family"] == family]
            (tmp_path / "packets" / "manifest.json").write_text(json.dumps(manifest))
            summary = run_agent_command(ROOT, tmp_path / "packets", tmp_path / "run", "noop", "true", timeout_s=30)
            self.assertEqual(summary["feasible_count"], 0)
            row = json.loads((tmp_path / "run" / "results.jsonl").read_text().splitlines()[0])
            self.assertIsNone(row["selected_attempt"])


if __name__ == "__main__":
    unittest.main()
