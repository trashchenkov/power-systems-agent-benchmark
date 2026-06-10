import json
import unittest
from pathlib import Path

from baselines.ev_v2g_outage_schedule.baseline import solve_case
from prototype.evaluators.evaluate_ev_v2g_outage_schedule import evaluate_case

ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "tasks/ev_v2g_outage_schedule/public/case_001/task.json"


class EVV2GOutageScheduleEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = json.loads(TASK_PATH.read_text(encoding="utf-8"))

    def test_baseline_submission_is_feasible(self) -> None:
        result = evaluate_case(self.task, solve_case(self.task))
        self.assertTrue(result["feasible"], result)

    def test_wrong_primary_command_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission['dispatch_kw']['t1']['ev_a'] += 4.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("dispatch_kw.t1.ev_a" in v for v in result["violations"]))

    def test_wrong_summary_value_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission['served_energy_kwh'] += 1.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("served_energy_kwh" in v for v in result["violations"]))

    def test_unknown_field_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["answer"] = "leak"
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))


if __name__ == "__main__":
    unittest.main()
