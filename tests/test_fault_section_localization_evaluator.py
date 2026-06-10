import json
import unittest
from pathlib import Path

from baselines.fault_section_localization.baseline import solve_case
from prototype.evaluators.evaluate_fault_section_localization import evaluate_case

ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "tasks/fault_section_localization/public/case_001/task.json"


class FaultSectionLocalizationEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = json.loads(TASK_PATH.read_text(encoding="utf-8"))

    def test_baseline_submission_is_feasible(self) -> None:
        result = evaluate_case(self.task, solve_case(self.task))
        self.assertTrue(result["feasible"], result)

    def test_wrong_primary_answer_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission['faulted_section']='s24'
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("faulted_section" in v for v in result["violations"]))

    def test_wrong_summary_value_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission['affected_customer_nodes']=[]
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("affected_customer_nodes" in v for v in result["violations"]))

    def test_unknown_field_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["answer"] = "leak"
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))


if __name__ == "__main__":
    unittest.main()
