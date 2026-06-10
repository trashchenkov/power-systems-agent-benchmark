import json
import unittest
from pathlib import Path

from baselines.ybus_construction.baseline import solve_case
from prototype.evaluators.evaluate_ybus_construction import evaluate_case


ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "tasks/ybus_construction/public/case_001/task.json"


class YbusConstructionEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = json.loads(TASK_PATH.read_text(encoding="utf-8"))

    def test_public_baseline_builds_correct_ybus(self) -> None:
        submission = solve_case(self.task)
        result = evaluate_case(self.task, submission)
        self.assertTrue(result["feasible"], result)
        self.assertEqual(result["score"], 1.0)
        self.assertAlmostEqual(result["max_abs_error"], 0.0, places=9)

    def test_rejects_wrong_bus_order(self) -> None:
        submission = solve_case(self.task)
        submission["buses"] = ["bus_2", "bus_1", "bus_3"]
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertIn("submission buses must match task bus order", result["violations"])

    def test_rejects_wrong_off_diagonal_sign(self) -> None:
        submission = solve_case(self.task)
        submission["ybus"][0][1] = {"re": 5.0, "im": -15.0}
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertIn("one or more Ybus entries exceed numeric tolerance", result["violations"])
        self.assertIn("bus_1,bus_2", result["entry_errors"])

    def test_rejects_missing_shunt_contribution(self) -> None:
        submission = solve_case(self.task)
        submission["ybus"][2][2]["im"] -= 0.04
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertIn("bus_3,bus_3", result["entry_errors"])


if __name__ == "__main__":
    unittest.main()
