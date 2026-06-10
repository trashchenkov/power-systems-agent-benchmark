import json
import unittest
from pathlib import Path

from baselines.en50160_voltage_compliance.baseline import solve_case
from prototype.evaluators.evaluate_en50160_voltage_compliance import evaluate_case


ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "tasks/en50160_voltage_compliance/public/case_001/task.json"


class EN50160VoltageComplianceEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = json.loads(TASK_PATH.read_text(encoding="utf-8"))

    def test_baseline_submission_is_feasible(self) -> None:
        result = evaluate_case(self.task, solve_case(self.task))
        self.assertTrue(result["feasible"], result)

    def test_wrong_compliance_decision_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["compliant"] = True
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("compliant" in v for v in result["violations"]))

    def test_missing_below_normal_timestamp_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["below_normal_timestamps"] = ["t03"]
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("below_normal_timestamps" in v for v in result["violations"]))

    def test_wrong_tap_recommendation_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["recommended_tap_change_pu"] = 0.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("recommended_tap_change_pu" in v for v in result["violations"]))


if __name__ == "__main__":
    unittest.main()
