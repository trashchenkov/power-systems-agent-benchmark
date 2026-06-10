import json
import unittest
from pathlib import Path

from baselines.fdi_state_estimation.baseline import solve_case
from prototype.evaluators.evaluate_fdi_state_estimation import evaluate_case


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_CASE = ROOT / "tasks/fdi_state_estimation/public/case_001/task.json"


class FDIStateEstimationEvaluatorTests(unittest.TestCase):
    def small_case(self):
        return {
            "task_id": "fdi_state_estimation_public_001",
            "residual_threshold": 3.0,
            "state_error_threshold": 0.05,
            "measurements": [
                {"id": "m12", "residual_norm": 0.8, "ground_truth_attack": False},
                {"id": "m23", "residual_norm": 4.2, "ground_truth_attack": True},
                {"id": "m31", "residual_norm": 3.7, "ground_truth_attack": True},
                {"id": "m14", "residual_norm": 1.1, "ground_truth_attack": False},
            ],
            "ground_truth_state": {"theta_2": -0.04, "theta_3": -0.07},
        }

    def test_accepts_correct_attack_labels_and_corrected_state(self):
        submission = {
            "attacked_measurements": ["m23", "m31"],
            "corrected_state": {"theta_2": -0.041, "theta_3": -0.069},
        }

        result = evaluate_case(self.small_case(), submission)

        self.assertTrue(result["feasible"], result["violations"])
        self.assertAlmostEqual(result["precision"], 1.0)
        self.assertAlmostEqual(result["recall"], 1.0)
        self.assertAlmostEqual(result["f1"], 1.0)
        self.assertLess(result["max_state_error"], 0.05)
        self.assertEqual(result["violations"], [])

    def test_rejects_missed_attack_measurement(self):
        submission = {
            "attacked_measurements": ["m23"],
            "corrected_state": {"theta_2": -0.041, "theta_3": -0.069},
        }

        result = evaluate_case(self.small_case(), submission)

        self.assertFalse(result["feasible"])
        self.assertIn("missed attacked measurement: m31", result["violations"])
        self.assertEqual(result["score"], 0.0)

    def test_rejects_bad_corrected_state(self):
        submission = {
            "attacked_measurements": ["m23", "m31"],
            "corrected_state": {"theta_2": 0.20, "theta_3": -0.069},
        }

        result = evaluate_case(self.small_case(), submission)

        self.assertFalse(result["feasible"])
        self.assertIn("max_state_error above threshold 0.050000", result["violations"])

    def test_public_baseline_is_feasible_for_public_case(self):
        case = json.loads(PUBLIC_CASE.read_text(encoding="utf-8"))

        submission = solve_case(case)
        result = evaluate_case(case, submission)

        self.assertTrue(result["feasible"], result["violations"])
        self.assertGreaterEqual(result["f1"], 1.0)


if __name__ == "__main__":
    unittest.main()
