import json
import unittest
from pathlib import Path

from baselines.rolling_microgrid_dispatch.baseline import solve_case
from prototype.evaluators.evaluate_rolling_microgrid_dispatch import evaluate_case

ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "tasks/rolling_microgrid_dispatch/public/case_001/task.json"


class RollingMicrogridDispatchEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = json.loads(TASK_PATH.read_text(encoding="utf-8"))

    def test_baseline_submission_is_feasible(self) -> None:
        result = evaluate_case(self.task, solve_case(self.task))
        self.assertTrue(result["feasible"], result)

    def test_wrong_dispatch_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission['dispatch'][next(iter(submission['dispatch']))]['diesel_mw'] += 1.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("diesel_mw" in v for v in result["violations"]))

    def test_wrong_total_or_voltage_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission['total_cost'] += 100.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("total_cost" in v for v in result["violations"]))

    def test_unknown_field_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["answer"] = "leak"
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))


if __name__ == "__main__":
    unittest.main()
