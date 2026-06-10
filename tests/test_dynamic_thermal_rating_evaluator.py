import json
import unittest
from pathlib import Path

from baselines.dynamic_thermal_rating.baseline import solve_case
from prototype.evaluators.evaluate_dynamic_thermal_rating import evaluate_case


ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "tasks/dynamic_thermal_rating/public/case_001/task.json"


class DynamicThermalRatingEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = json.loads(TASK_PATH.read_text(encoding="utf-8"))

    def test_baseline_submission_is_feasible(self) -> None:
        result = evaluate_case(self.task, solve_case(self.task))
        self.assertTrue(result["feasible"], result)

    def test_wrong_limiting_timestamp_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["limiting_timestamp"] = "t00"
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("limiting_timestamp" in v for v in result["violations"]))

    def test_wrong_ampacity_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["ampacity_by_timestamp_a"]["t01"] += 20.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("t01" in v for v in result["violations"]))

    def test_missing_overload_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["overload_timestamps"] = []
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("overload_timestamps" in v for v in result["violations"]))


if __name__ == "__main__":
    unittest.main()
