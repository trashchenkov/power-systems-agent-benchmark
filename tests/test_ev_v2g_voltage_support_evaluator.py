import json
import unittest
from pathlib import Path

from baselines.ev_v2g_voltage_support.baseline import solve_case
from prototype.evaluators.evaluate_ev_v2g_voltage_support import evaluate_case

ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "tasks/ev_v2g_voltage_support/public/case_001/task.json"


class EVV2GVoltageSupportEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = json.loads(TASK_PATH.read_text(encoding="utf-8"))

    def test_baseline_submission_is_feasible(self) -> None:
        result = evaluate_case(self.task, solve_case(self.task))
        self.assertTrue(result["feasible"], result)

    def test_wrong_primary_command_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission['q_dispatch_kvar']['bus_2'] += 1.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("q_dispatch_kvar.bus_2" in v for v in result["violations"]))

    def test_wrong_summary_value_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission['corrected_voltage_pu']['bus_2'] += 0.02
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("corrected_voltage_pu.bus_2" in v for v in result["violations"]))

    def test_unknown_field_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["answer"] = "leak"
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))


if __name__ == "__main__":
    unittest.main()
