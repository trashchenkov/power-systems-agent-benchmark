import json
import unittest
from pathlib import Path

from baselines.islanded_microgrid_pq_dispatch.baseline import solve_case
from prototype.evaluators.evaluate_islanded_microgrid_pq_dispatch import evaluate_case

ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "tasks/islanded_microgrid_pq_dispatch/public/case_001/task.json"


class IslandedMicrogridPQDispatchEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = json.loads(TASK_PATH.read_text(encoding="utf-8"))

    def test_baseline_submission_is_feasible(self) -> None:
        result = evaluate_case(self.task, solve_case(self.task))
        self.assertTrue(result["feasible"], result)

    def test_wrong_dispatch_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission['dispatch']['inverter']['q_mvar'] += 1.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("dispatch.inverter.q_mvar" in v for v in result["violations"]))

    def test_wrong_total_or_voltage_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission['voltage_pu'] += 0.1
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("voltage_pu" in v for v in result["violations"]))

    def test_unknown_field_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["answer"] = "leak"
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))


if __name__ == "__main__":
    unittest.main()
