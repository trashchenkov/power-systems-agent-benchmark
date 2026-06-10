import json
import unittest
from pathlib import Path

from baselines.frt_compliance.baseline import solve_case
from prototype.evaluators.evaluate_frt_compliance import evaluate_case


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_CASE = ROOT / "tasks/frt_compliance/public/case_001/task.json"


class FRTComplianceEvaluatorTests(unittest.TestCase):
    def small_case(self):
        return {
            "task_id": "frt_compliance_public_001",
            "ride_through_curve": [
                {"max_duration_s": 0.15, "min_voltage_pu": 0.20},
                {"max_duration_s": 0.70, "min_voltage_pu": 0.50},
                {"max_duration_s": 2.00, "min_voltage_pu": 0.85},
            ],
            "reactive_current_requirement": {
                "voltage_below_pu": 0.90,
                "min_iq_pu": 0.20,
                "response_deadline_s": 0.10,
            },
            "event_trace": [
                {"time_s": 0.00, "voltage_pu": 1.00, "iq_pu": 0.00, "connected": True},
                {"time_s": 0.05, "voltage_pu": 0.55, "iq_pu": 0.10, "connected": True},
                {"time_s": 0.12, "voltage_pu": 0.55, "iq_pu": 0.25, "connected": True},
                {"time_s": 0.55, "voltage_pu": 0.90, "iq_pu": 0.22, "connected": True},
                {"time_s": 0.80, "voltage_pu": 1.00, "iq_pu": 0.00, "connected": True},
            ],
        }

    def test_accepts_trace_that_rides_through_and_supports_reactive_current(self):
        result = evaluate_case(self.small_case(), {"declared_compliant": True})

        self.assertTrue(result["feasible"], result["violations"])
        self.assertTrue(result["ride_through_pass"])
        self.assertTrue(result["reactive_current_pass"])
        self.assertEqual(result["violations"], [])
        self.assertEqual(result["score"], 1.0)

    def test_rejects_disconnection_inside_ride_through_envelope(self):
        case = self.small_case()
        case["event_trace"][2]["connected"] = False

        result = evaluate_case(case, {"declared_compliant": True})

        self.assertFalse(result["feasible"])
        self.assertIn("disconnected inside ride-through envelope at 0.120000 s", result["violations"])
        self.assertEqual(result["score"], 0.0)

    def test_rejects_missing_reactive_current_support_after_deadline(self):
        case = self.small_case()
        case["event_trace"][2]["iq_pu"] = 0.05
        case["event_trace"][3]["iq_pu"] = 0.05

        result = evaluate_case(case, {"declared_compliant": True})

        self.assertFalse(result["feasible"])
        self.assertIn("reactive current support below 0.200000 pu after deadline", result["violations"])

    def test_public_baseline_is_feasible_for_public_case(self):
        case = json.loads(PUBLIC_CASE.read_text(encoding="utf-8"))

        submission = solve_case(case)
        result = evaluate_case(case, submission)

        self.assertTrue(result["feasible"], result["violations"])
        self.assertTrue(result["ride_through_pass"])


if __name__ == "__main__":
    unittest.main()
