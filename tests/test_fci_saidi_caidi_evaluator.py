import json
import unittest
from pathlib import Path

from baselines.fci_saidi_caidi.baseline import solve_case
from prototype.evaluators.evaluate_fci_saidi_caidi import evaluate_case

ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "tasks/fci_saidi_caidi/public/case_001/task.json"


class FCISAIDICAIDIEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = json.loads(TASK_PATH.read_text(encoding="utf-8"))

    def test_baseline_submission_is_feasible(self) -> None:
        result = evaluate_case(self.task, solve_case(self.task))
        self.assertTrue(result["feasible"], result)

    def test_wrong_primary_answer_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission['with_fci']['saidi_min_per_customer_year'] += 1.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("with_fci.saidi" in v for v in result["violations"]))

    def test_wrong_summary_value_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission['caidi_improvement_min_per_interruption'] += 1.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("caidi_improvement" in v for v in result["violations"]))

    def test_unknown_field_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["answer"] = "leak"
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))


if __name__ == "__main__":
    unittest.main()
