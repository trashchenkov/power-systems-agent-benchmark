import json
import unittest
from pathlib import Path

from baselines.earth_fault_calculation.baseline import solve_case
from prototype.evaluators.evaluate_earth_fault_calculation import evaluate_case


ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "tasks/earth_fault_calculation/public/case_001/task.json"


class EarthFaultCalculationEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = json.loads(TASK_PATH.read_text(encoding="utf-8"))

    def test_baseline_submission_is_feasible(self) -> None:
        result = evaluate_case(self.task, solve_case(self.task))
        self.assertTrue(result["feasible"], result)
        self.assertEqual(result["score"], 1.0)

    def test_wrong_zero_sequence_current_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["sequence_currents_ka"]["i0"]["mag_ka"] *= 0.8
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("i0.mag_ka" in v for v in result["violations"]))

    def test_fault_current_angle_error_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["fault_current_ka"]["angle_deg"] += 5.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("fault_current_ka.angle_deg" in v for v in result["violations"]))

    def test_missing_sequence_object_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["sequence_currents_ka"].pop("i2")
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertIn("missing required field: sequence_currents_ka.i2", result["violations"])

    def test_unknown_answer_field_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["answer"] = {"i1_ka": 3.2}
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))


if __name__ == "__main__":
    unittest.main()
