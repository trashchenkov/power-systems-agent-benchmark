import json
import unittest
from pathlib import Path

from baselines.breaker_relay_short_circuit.baseline import solve_case
from prototype.evaluators.evaluate_breaker_relay_short_circuit import compute_fault_study, evaluate_case


ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "tasks/breaker_relay_short_circuit/public/case_001/task.json"


class BreakerRelayShortCircuitEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = json.loads(TASK_PATH.read_text(encoding="utf-8"))

    def test_public_baseline_is_feasible(self) -> None:
        submission = solve_case(self.task)
        result = evaluate_case(self.task, submission)
        self.assertTrue(result["feasible"], result)
        self.assertEqual(result["score"], 1.0)

    def test_rejects_wrong_fault_current(self) -> None:
        submission = solve_case(self.task)
        submission["max_3ph_fault_ka"] += 1.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertIn("max_3ph_fault_ka does not match recomputed study", result["violations"])

    def test_rejects_undersized_breaker(self) -> None:
        submission = solve_case(self.task)
        submission["breaker_interrupting_rating_ka"] = 8.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertIn("breaker_interrupting_rating_ka below required safety margin", result["violations"])

    def test_rejects_nonstandard_breaker_rating(self) -> None:
        submission = solve_case(self.task)
        submission["breaker_interrupting_rating_ka"] = 13.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertIn("breaker_interrupting_rating_ka must be one of the available standard ratings", result["violations"])

    def test_rejects_pickup_without_fault_sensitivity(self) -> None:
        submission = solve_case(self.task)
        study = compute_fault_study(self.task)
        submission["relay_pickup_a_primary"] = study["relay_pickup_max_a"] + 10.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertIn("relay_pickup_a_primary above minimum-fault sensitivity maximum", result["violations"])


if __name__ == "__main__":
    unittest.main()
