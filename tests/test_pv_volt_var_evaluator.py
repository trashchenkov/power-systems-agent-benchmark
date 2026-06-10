import json
import unittest
from pathlib import Path

from baselines.pv_volt_var.baseline import solve_case
from prototype.evaluators.evaluate_pv_volt_var import evaluate_case


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_CASE = ROOT / "tasks/pv_volt_var/public/case_001/task.json"


class PVVoltVarEvaluatorTests(unittest.TestCase):
    def small_case(self):
        return {
            "task_id": "pv_volt_var_public_001",
            "voltage_limits_pu": {"min": 0.95, "max": 1.05},
            "monotonic_tolerance": 1e-9,
            "timesteps": [
                {"id": "t_low", "base_voltage_pu": 0.940, "pv_kw": 60.0, "inverter_kva": 100.0, "voltage_sensitivity_pu_per_kvar": 0.00070},
                {"id": "t_nom", "base_voltage_pu": 1.000, "pv_kw": 80.0, "inverter_kva": 100.0, "voltage_sensitivity_pu_per_kvar": 0.00055},
                {"id": "t_high", "base_voltage_pu": 1.070, "pv_kw": 60.0, "inverter_kva": 100.0, "voltage_sensitivity_pu_per_kvar": 0.00070},
            ],
        }

    def ieee_like_curve(self):
        return {
            "volt_var_curve": [
                {"voltage_pu": 0.94, "q_fraction": 1.0},
                {"voltage_pu": 0.97, "q_fraction": 0.0},
                {"voltage_pu": 1.03, "q_fraction": 0.0},
                {"voltage_pu": 1.06, "q_fraction": -1.0},
            ]
        }

    def test_accepts_monotonic_curve_that_repairs_voltage_sag_and_swell(self):
        result = evaluate_case(self.small_case(), self.ieee_like_curve())

        self.assertTrue(result["feasible"], result["violations"])
        self.assertEqual(result["voltage_violation_timesteps"], [])
        self.assertEqual(result["q_limit_violations"], [])
        self.assertAlmostEqual(result["timeseries"]["t_low"]["q_command_kvar"], 80.0)
        self.assertAlmostEqual(result["timeseries"]["t_high"]["q_command_kvar"], -80.0)
        self.assertGreater(result["score"], 0.9)
        self.assertLessEqual(result["score"], 1.0)

    def test_rejects_non_monotonic_volt_var_curve(self):
        case = self.small_case()
        submission = {
            "volt_var_curve": [
                {"voltage_pu": 0.94, "q_fraction": 0.0},
                {"voltage_pu": 1.00, "q_fraction": 0.5},
                {"voltage_pu": 1.06, "q_fraction": -1.0},
            ]
        }

        result = evaluate_case(case, submission)

        self.assertFalse(result["feasible"])
        self.assertIn("volt_var_curve must be monotonic non-increasing in q_fraction", result["violations"])
        self.assertEqual(result["score"], 0.0)

    def test_zero_reactive_control_leaves_voltage_violations(self):
        case = self.small_case()
        submission = {
            "volt_var_curve": [
                {"voltage_pu": 0.94, "q_fraction": 0.0},
                {"voltage_pu": 1.06, "q_fraction": 0.0},
            ]
        }

        result = evaluate_case(case, submission)

        self.assertFalse(result["feasible"])
        self.assertEqual(result["voltage_violation_timesteps"], ["t_low", "t_high"])

    def test_public_baseline_is_feasible_for_public_case(self):
        case = json.loads(PUBLIC_CASE.read_text(encoding="utf-8"))

        submission = solve_case(case)
        result = evaluate_case(case, submission)

        self.assertTrue(result["feasible"], result["violations"])
        self.assertEqual(result["voltage_violation_timesteps"], [])


if __name__ == "__main__":
    unittest.main()
