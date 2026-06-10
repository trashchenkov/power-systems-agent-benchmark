import json
import unittest
from pathlib import Path

from baselines.power_quality_event_classification.baseline import solve_case
from prototype.evaluators.evaluate_power_quality_event_classification import evaluate_case


ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "tasks/power_quality_event_classification/public/case_001/task.json"


class PowerQualityEventClassificationEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = json.loads(TASK_PATH.read_text(encoding="utf-8"))

    def test_baseline_submission_is_feasible(self) -> None:
        result = evaluate_case(self.task, solve_case(self.task))
        self.assertTrue(result["feasible"], result)

    def test_wrong_event_class_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["event_class"] = "voltage_swell"
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("event_class" in v for v in result["violations"]))

    def test_wrong_event_start_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["start_timestamp_ms"] = 60
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("start_timestamp_ms" in v for v in result["violations"]))

    def test_wrong_min_voltage_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["min_voltage_pu"] = 0.7
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("min_voltage_pu" in v for v in result["violations"]))


if __name__ == "__main__":
    unittest.main()
