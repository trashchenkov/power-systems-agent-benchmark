import json
import unittest
from pathlib import Path

from baselines.dispatch_uncertainty.baseline import solve_case
from prototype.evaluators.evaluate_dispatch_uncertainty import evaluate_case


ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "tasks/dispatch_uncertainty/public/case_001/task.json"


class DispatchUncertaintyEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = json.loads(TASK_PATH.read_text(encoding="utf-8"))

    def test_baseline_submission_is_feasible(self) -> None:
        result = evaluate_case(self.task, solve_case(self.task))
        self.assertTrue(result["feasible"], result)

    def test_under_reserved_dispatch_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["dispatch_mw"]["g2"]["t2"] -= 2.0
        submission["worst_case_margin_mw"]["t2"] -= 2.0
        submission["total_cost"] -= 72.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("reserve" in v or "dispatch_mw.g2.t2" in v for v in result["violations"]))

    def test_generator_bounds_are_enforced(self) -> None:
        submission = solve_case(self.task)
        submission["dispatch_mw"]["g1"]["t1"] = 90.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("bounds" in v for v in result["violations"]))

    def test_wrong_total_cost_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["total_cost"] += 10.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("total_cost" in v for v in result["violations"]))


if __name__ == "__main__":
    unittest.main()
