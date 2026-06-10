import json
import math
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

    def test_max_current_uses_cmax_and_bolted_fault(self) -> None:
        case = self.task["short_circuit_case"]
        z = sum(complex(c.get("r_pu", 0.0), c.get("x_pu", 0.0)) for c in case["positive_sequence_impedances_pu"])
        i_base = case["base_mva"] / (math.sqrt(3) * case["voltage_kv"])
        expected_ik_max = case["voltage_factor_cmax"] / abs(z) * i_base
        submission = solve_case(self.task)
        self.assertAlmostEqual(submission["ik_max_ka"], expected_ik_max, places=4)
        # Maximum must exceed minimum: cmax > cmin and no fault resistance in the path.
        self.assertGreater(submission["ik_max_ka"], submission["ik_min_ka"])

    def test_min_current_includes_fault_resistance(self) -> None:
        case = self.task["short_circuit_case"]
        z = sum(complex(c.get("r_pu", 0.0), c.get("x_pu", 0.0)) for c in case["positive_sequence_impedances_pu"])
        z_min = z + complex(case["fault_resistance_pu"], 0.0)
        i_base = case["base_mva"] / (math.sqrt(3) * case["voltage_kv"])
        expected_ik_min = case["voltage_factor_cmin"] / abs(z_min) * i_base
        submission = solve_case(self.task)
        self.assertAlmostEqual(submission["ik_min_ka"], expected_ik_min, places=4)

    def test_current_error_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["ik_max_ka"] += 0.5
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("ik_max_ka" in v for v in result["violations"]))

    def test_missing_min_current_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission.pop("ik_min_ka")
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertIn("missing required field: ik_min_ka", result["violations"])

    def test_unknown_answer_field_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["expected_submission"] = {"leak": True}
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))


if __name__ == "__main__":
    unittest.main()
