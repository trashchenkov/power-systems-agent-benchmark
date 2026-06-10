import json
import unittest
from pathlib import Path

from baselines.overcurrent_protection.baseline import solve_case
from prototype.evaluators.evaluate_overcurrent_protection import evaluate_case


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_CASE = ROOT / "tasks/overcurrent_protection/public/case_001/task.json"


class OvercurrentProtectionEvaluatorTests(unittest.TestCase):
    def small_case(self):
        return {
            "task_id": "overcurrent_protection_public_001",
            "max_load_current_a": 420.0,
            "min_fault_current_a": 1800.0,
            "ct_ratio_primary_per_secondary": 100.0,
            "load_margin_multiplier": 1.2,
            "min_sensitivity_factor": 1.5,
            "downstream_time_delay_s": 0.35,
            "selectivity_margin_s": 0.30,
            "relay_secondary_pickup_range_a": {"min": 1.0, "max": 10.0},
            "time_delay_range_s": {"min": 0.0, "max": 2.0},
        }

    def test_accepts_selective_and_sensitive_setting(self):
        case = self.small_case()
        submission = {"pickup_current_a": 600.0, "time_delay_s": 0.70}

        result = evaluate_case(case, submission)

        self.assertTrue(result["feasible"], result["violations"])
        self.assertEqual(result["violations"], [])
        self.assertAlmostEqual(result["sensitivity_factor"], 3.0)
        self.assertAlmostEqual(result["secondary_pickup_a"], 6.0)
        self.assertGreater(result["score"], 0.9)
        self.assertLessEqual(result["score"], 1.0)

    def test_rejects_pickup_below_load_margin(self):
        case = self.small_case()
        submission = {"pickup_current_a": 480.0, "time_delay_s": 0.70}

        result = evaluate_case(case, submission)

        self.assertFalse(result["feasible"])
        self.assertIn("pickup_current_a below load margin minimum 504.000000 A", result["violations"])
        self.assertEqual(result["score"], 0.0)

    def test_rejects_insufficient_fault_sensitivity(self):
        case = self.small_case()
        submission = {"pickup_current_a": 1300.0, "time_delay_s": 0.70}

        result = evaluate_case(case, submission)

        self.assertFalse(result["feasible"])
        self.assertIn("sensitivity factor 1.384615 below minimum 1.500000", result["violations"])

    def test_rejects_insufficient_selectivity_time_margin(self):
        case = self.small_case()
        submission = {"pickup_current_a": 600.0, "time_delay_s": 0.55}

        result = evaluate_case(case, submission)

        self.assertFalse(result["feasible"])
        self.assertIn("time_delay_s below selectivity minimum 0.650000 s", result["violations"])

    def test_public_baseline_is_feasible_for_public_case(self):
        case = json.loads(PUBLIC_CASE.read_text(encoding="utf-8"))

        submission = solve_case(case)
        result = evaluate_case(case, submission)

        self.assertTrue(result["feasible"], result["violations"])
        self.assertEqual(result["violations"], [])


if __name__ == "__main__":
    unittest.main()
