import json
import unittest
from pathlib import Path

from baselines.bess_ancillary_response.baseline import solve_case
from prototype.evaluators.evaluate_bess_ancillary_response import evaluate_case

ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "tasks/bess_ancillary_response/public/case_001/task.json"


class BESSAncillaryResponseEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = json.loads(TASK_PATH.read_text(encoding="utf-8"))

    def test_baseline_submission_is_feasible(self) -> None:
        result = evaluate_case(self.task, solve_case(self.task))
        self.assertTrue(result["feasible"], result)

    def test_wrong_primary_command_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission['p_response_mw']['t0'] += 1.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("p_response_mw.t0" in v for v in result["violations"]))

    def test_wrong_summary_value_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission['final_soc_mwh'] += 0.1
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("final_soc_mwh" in v for v in result["violations"]))

    def test_unknown_field_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["answer"] = "leak"
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))


if __name__ == "__main__":
    unittest.main()
