import json
import unittest
from pathlib import Path

from baselines.pf_voltage_repair.baseline import solve_case
from prototype.evaluators.evaluate_voltage_repair import evaluate_case


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_CASE = ROOT / "tasks/pf_voltage_repair/public/case_001/task.json"


class VoltageRepairBaselineTests(unittest.TestCase):
    def test_baseline_returns_feasible_submission_for_public_case(self):
        case = json.loads(PUBLIC_CASE.read_text(encoding="utf-8"))

        submission = solve_case(case)
        result = evaluate_case(case, submission)

        self.assertTrue(result["feasible"], result["violations"])
        self.assertIn("actions", submission)
        self.assertLessEqual(result["action_cost"], 20.0)


if __name__ == "__main__":
    unittest.main()
