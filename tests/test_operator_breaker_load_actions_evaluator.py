import json
import unittest
from pathlib import Path
from baselines.operator_breaker_load_actions.baseline import solve_case
from prototype.evaluators.evaluate_operator_breaker_load_actions import evaluate_case
ROOT=Path(__file__).resolve().parents[1]
TASK_PATH=ROOT/"tasks/operator_breaker_load_actions/public/case_001/task.json"
class OperatorBreakerLoadActionsTests(unittest.TestCase):
    def setUp(self): self.task=json.loads(TASK_PATH.read_text(encoding="utf-8"))
    def test_baseline_submission_is_feasible(self):
        result=evaluate_case(self.task, solve_case(self.task)); self.assertTrue(result["feasible"], result)
    def test_wrong_answer_is_rejected(self):
        submission=solve_case(self.task); submission['selected_actions']=['shed_bus2_10']; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("selected_actions" in v for v in result["violations"]), result)
    def test_unknown_field_is_rejected(self):
        submission=solve_case(self.task); submission["answer"]="leak"; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))
if __name__=="__main__": unittest.main()
