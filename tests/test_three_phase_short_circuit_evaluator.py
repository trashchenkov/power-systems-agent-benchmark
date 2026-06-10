import json
import unittest
from pathlib import Path

from baselines.three_phase_short_circuit.baseline import solve_case
from prototype.evaluators.evaluate_three_phase_short_circuit import evaluate_case


ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "tasks/three_phase_short_circuit/public/case_001/task.json"


class ThreePhaseShortCircuitEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = json.loads(TASK_PATH.read_text(encoding="utf-8"))

    def test_baseline_submission_is_feasible(self) -> None:
        result = evaluate_case(self.task, solve_case(self.task))
        self.assertTrue(result["feasible"], result)
        self.assertEqual(result["score"], 1.0)

    def test_current_error_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["fault_current_ka"] += 0.5
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("fault_current_ka" in v for v in result["violations"]))

    def test_missing_fault_mva_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission.pop("fault_mva")
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertIn("missing required field: fault_mva", result["violations"])

    def test_unknown_answer_field_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["expected_submission"] = {"leak": True}
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))


if __name__ == "__main__":
    unittest.main()
