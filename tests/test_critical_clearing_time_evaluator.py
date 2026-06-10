import json
import unittest
from pathlib import Path
from baselines.critical_clearing_time.baseline import solve_case
from prototype.evaluators.evaluate_critical_clearing_time import evaluate_case
ROOT=Path(__file__).resolve().parents[1]
TASK_PATH=ROOT/"tasks/critical_clearing_time/public/case_001/task.json"
class CriticalClearingTimeEvaluatorTests(unittest.TestCase):
    def setUp(self): self.task=json.loads(TASK_PATH.read_text(encoding="utf-8"))
    def test_baseline_submission_is_feasible(self):
        result=evaluate_case(self.task, solve_case(self.task)); self.assertTrue(result["feasible"], result)
    def test_wrong_primary_answer_is_rejected(self):
        submission=solve_case(self.task); submission['critical_clearing_time_s'] += 0.01; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("critical_clearing_time_s" in v for v in result["violations"]), result)
    def test_wrong_summary_value_is_rejected(self):
        submission=solve_case(self.task); submission['limiting_case']='tc_120'; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("limiting_case" in v for v in result["violations"]), result)
    def test_unknown_field_is_rejected(self):
        submission=solve_case(self.task); submission["answer"]="leak"; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))
if __name__=="__main__": unittest.main()
