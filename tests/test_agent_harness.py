import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.evaluate_submission import discover_executable_cases, evaluate_submission_file
from scripts.run_public_baselines import run_public_baselines
from scripts.prepare_agent_tasks import prepare_agent_tasks
from scripts.run_agent_command import run_agent_command


ROOT = Path(__file__).resolve().parents[1]

# Hidden cases are intentionally untracked (.gitignore: **/hidden/), so fresh
# clones lack them; hidden-dependent tests only run where the material exists.
HIDDEN_CASES_PRESENT = any(ROOT.glob("tasks/*/hidden/case_*/task.json"))


class AgentHarnessTests(unittest.TestCase):
    def test_discovers_all_executable_public_cases(self):
        cases = discover_executable_cases(ROOT)
        families = [case.family for case in cases]

        self.assertEqual(len(families), 41)
        self.assertEqual(len(set(families)), 41)
        for required_family in {
            "contingency_screening",
            "fdi_state_estimation",
            "flisr_restoration",
            "frt_compliance",
            "overcurrent_protection",
            "pf_voltage_repair",
            "pv_volt_var",
            "bess_ancillary_response",
            "dynamic_thermal_rating",
            "ybus_construction",
        }:
            self.assertIn(required_family, families)

    def test_public_tasks_have_bilingual_english_and_russian_fields(self):
        cases = discover_executable_cases(ROOT)

        self.assertEqual(len(cases), 41)
        for case in cases:
            task = json.loads(case.task_path.read_text(encoding="utf-8"))
            bilingual = task.get("bilingual")
            self.assertIsInstance(bilingual, dict, case.task_path)
            for key in ("title", "objective", "instructions"):
                self.assertIsInstance(bilingual.get(key), dict, case.task_path)
                self.assertTrue(str(bilingual[key].get("en", "")).strip(), case.task_path)
                self.assertTrue(str(bilingual[key].get("ru", "")).strip(), case.task_path)

    def test_evaluates_one_submission_with_family_dispatch(self):
        result = evaluate_submission_file(
            ROOT / "tasks/fdi_state_estimation/public/case_001/task.json",
            ROOT / "tasks/fdi_state_estimation/public/case_001/sample_submission.json",
        )

        self.assertTrue(result["feasible"], result["violations"])
        self.assertEqual(result["task_id"], "fdi_state_estimation_public_001")
        self.assertEqual(result["score"], 1.0)

    def test_evaluate_submission_cli_runs_from_repository_root(self):
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/evaluate_submission.py",
                "tasks/fdi_state_estimation/public/case_001/task.json",
                "tasks/fdi_state_estimation/public/case_001/sample_submission.json",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("fdi_state_estimation_public_001", completed.stdout)

    def test_public_baseline_runner_writes_submissions_and_jsonl_results(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            summary = run_public_baselines(ROOT, out_dir)

            self.assertEqual(summary["case_count"], 41)
            self.assertEqual(summary["feasible_count"], 41)
            self.assertIn("mean_score", summary)
            self.assertNotIn("total_score", summary)
            self.assertGreaterEqual(summary["mean_score"], 0.0)
            self.assertLessEqual(summary["mean_score"], 1.0)
            self.assertTrue((out_dir / "results.jsonl").exists())
            self.assertTrue((out_dir / "submissions/fdi_state_estimation__case_001.json").exists())
            rows = [json.loads(line) for line in (out_dir / "results.jsonl").read_text().splitlines()]
            self.assertEqual(len(rows), 41)
            self.assertTrue(all(row["result"]["feasible"] for row in rows))

    def test_prepare_agent_tasks_creates_portable_task_packets_without_agent_lock_in(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            summary = prepare_agent_tasks(ROOT, out_dir)

            self.assertEqual(summary["case_count"], 41)
            prompt = (out_dir / "fdi_state_estimation__public__case_001/instructions.md").read_text(encoding="utf-8")
            self.assertIn("You are solving one executable power-systems benchmark task", prompt)
            self.assertIn("Write exactly one JSON file", prompt)
            self.assertNotIn("Codex", prompt)
            self.assertNotIn("OpenCode", prompt)
            task = json.loads((out_dir / "bess_ancillary_response__public__case_001/task.json").read_text(encoding="utf-8"))
            self.assertNotIn("expected_submission", task)
            self.assertNotIn("baseline_submission", task)
            self.assertIn("calculation_spec", task.get("public_inputs", {}))
            executable_task = json.loads((out_dir / "breaker_relay_short_circuit__public__case_001/task.json").read_text(encoding="utf-8"))
            self.assertNotIn("expected_submission", executable_task)
            self.assertNotIn("baseline_submission", executable_task)
            self.assertIn("short_circuit_case", executable_task)
            manifest_packet = next(packet for packet in summary["packets"] if packet["family"] == "breaker_relay_short_circuit")
            self.assertNotIn("source_task_path", manifest_packet)
            self.assertNotIn("evaluation_command", manifest_packet)
            self.assertTrue((out_dir / "fdi_state_estimation__public__case_001/task.json").exists())
            self.assertTrue((out_dir / "manifest.json").exists())

    def test_discovers_requested_public_and_hidden_splits(self):
        cases = discover_executable_cases(ROOT, splits=("public", "hidden"))

        self.assertTrue(all(case.split in {"public", "hidden"} for case in cases))
        self.assertEqual(sum(1 for case in cases if case.split == "public"), 41)

    def test_prepare_hidden_agent_tasks_uses_split_names_and_does_not_copy_samples(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            hidden_case = tmp / "tasks/pf_voltage_repair/hidden/case_901"
            hidden_case.mkdir(parents=True)
            hidden_task = json.loads((ROOT / "tasks/pf_voltage_repair/public/case_001/task.json").read_text())
            hidden_task["task_id"] = "pf_voltage_repair_hidden_901"
            (hidden_case / "task.json").write_text(json.dumps(hidden_task), encoding="utf-8")
            (hidden_case / "sample_submission.json").write_text("{}", encoding="utf-8")
            out_dir = tmp / "packets"

            summary = prepare_agent_tasks(tmp, out_dir, splits=("hidden",))

            self.assertEqual(summary["case_count"], 1)
            packet = out_dir / "pf_voltage_repair__hidden__case_901"
            self.assertTrue((packet / "task.json").exists())
            self.assertFalse((packet / "sample_submission.json").exists())
            manifest_packet = summary["packets"][0]
            self.assertEqual(manifest_packet["split"], "hidden")
            self.assertNotIn("source_task_path", manifest_packet)
            self.assertNotIn("evaluation_command", manifest_packet)
            instructions = (packet / "instructions.md").read_text(encoding="utf-8")
            self.assertNotIn("evaluate_submission.py", instructions)
            self.assertNotIn("source_task_path", instructions)

    @unittest.skipUnless(HIDDEN_CASES_PRESENT, "hidden cases are not distributed with the repository")
    def test_repository_contains_first_harder_hidden_cases(self):
        cases = discover_executable_cases(ROOT, splits=("hidden",))
        families = sorted(case.family for case in cases)

        self.assertGreaterEqual(len(cases), 3)
        self.assertIn("contingency_screening", families)
        self.assertIn("pv_volt_var", families)
        self.assertIn("pf_voltage_repair", families)

    @unittest.skipUnless(HIDDEN_CASES_PRESENT, "hidden cases are not distributed with the repository")
    def test_hidden_agent_packets_redact_evaluator_only_payloads(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            summary = prepare_agent_tasks(ROOT, out_dir, splits=("hidden",))

            self.assertGreaterEqual(summary["case_count"], 3)
            for packet in summary["packets"]:
                task = json.loads(Path(packet["task_path"]).read_text(encoding="utf-8"))
                self.assertNotIn("evaluator_only", task)
                self.assertNotIn("sample_submission", task)
                self.assertNotIn("ground_truth_state", task)
                for measurement in task.get("measurements", []):
                    self.assertNotIn("ground_truth_attack", measurement)

    def test_command_agent_runner_is_cli_agnostic_and_evaluates_outputs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            packets_dir = tmp / "packets"
            run_dir = tmp / "run"
            prepare_agent_tasks(ROOT, packets_dir)
            # The fake agent injects the repo root itself: the harness no longer
            # exposes BENCH_ROOT or repo PYTHONPATH inside the sandbox.
            command = (
                f"PYTHONPATH={ROOT} {sys.executable} -c \""
                "import json, os; "
                "from pathlib import Path; "
                "from scripts.run_public_baselines import solve_with_baseline; "
                "assert 'BENCH_ROOT' not in os.environ, 'sandbox must not expose the repo root'; "
                f"source=Path('{ROOT}')/'tasks'/os.environ['BENCH_FAMILY']/os.environ['BENCH_SPLIT']/os.environ['BENCH_CASE_ID']/'task.json'; "
                "packet_task=json.loads(Path(os.environ['BENCH_TASK_PATH']).read_text()); "
                "task=json.loads(source.read_text()) if source.exists() else packet_task; "
                "submission=solve_with_baseline(os.environ['BENCH_FAMILY'], task); "
                "Path(os.environ['BENCH_SUBMISSION_PATH']).write_text(json.dumps(submission))"
                "\""
            )

            summary = run_agent_command(ROOT, packets_dir, run_dir, "fake-baseline-agent", command)

            self.assertEqual(summary["case_count"], 41)
            self.assertEqual(summary["feasible_count"], 41)
            self.assertIn("mean_score", summary)
            self.assertNotIn("total_score", summary)
            self.assertGreaterEqual(summary["mean_score"], 0.0)
            self.assertLessEqual(summary["mean_score"], 1.0)
            self.assertTrue((run_dir / "results.jsonl").exists())
            self.assertTrue((run_dir / "submissions/contingency_screening__public__case_001.json").exists())


if __name__ == "__main__":
    unittest.main()
