import json
import tempfile
import unittest
from pathlib import Path

from prototype.evaluators.evaluate_voltage_repair import evaluate_case


class VoltageRepairEvaluatorTests(unittest.TestCase):
    def test_valid_reactive_support_action_removes_voltage_violation(self):
        case = {
            "task_id": "pf_voltage_repair_public_001",
            "base_voltage_pu": {"bus_1": 1.0, "bus_2": 0.925},
            "limits": {"min_vm_pu": 0.95, "max_vm_pu": 1.05},
            "sensitivities": {"bus_2": {"q_cap_mvar": 0.006}},
            "action_bounds": {"q_cap_mvar": {"min": 0.0, "max": 20.0, "cost_per_unit": 1.0}},
        }
        submission = {"actions": {"bus_2": {"q_cap_mvar": 5.0}}}

        result = evaluate_case(case, submission)

        self.assertTrue(result["feasible"])
        self.assertEqual(result["violations"], [])
        self.assertAlmostEqual(result["final_voltage_pu"]["bus_2"], 0.955)
        self.assertEqual(result["score"], 0.95)

    def test_out_of_bounds_action_is_rejected_before_scoring(self):
        case = {
            "task_id": "pf_voltage_repair_public_001",
            "base_voltage_pu": {"bus_2": 0.925},
            "limits": {"min_vm_pu": 0.95, "max_vm_pu": 1.05},
            "sensitivities": {"bus_2": {"q_cap_mvar": 0.006}},
            "action_bounds": {"q_cap_mvar": {"min": 0.0, "max": 20.0, "cost_per_unit": 1.0}},
        }
        submission = {"actions": {"bus_2": {"q_cap_mvar": 25.0}}}

        result = evaluate_case(case, submission)

        self.assertFalse(result["feasible"])
        self.assertIn("bus_2.q_cap_mvar out of bounds", result["violations"])
        self.assertEqual(result["score"], 0.0)


if __name__ == "__main__":
    unittest.main()
