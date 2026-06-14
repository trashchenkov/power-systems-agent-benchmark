import json
import unittest
from pathlib import Path
from baselines.min_synchronous_share.baseline import solve_case
from prototype.evaluators.evaluate_min_synchronous_share import evaluate_case
ROOT=Path(__file__).resolve().parents[1]
TASK_PATH=ROOT/"tasks/min_synchronous_share/public/case_001/task.json"
class MinSynchronousShareEvaluatorTests(unittest.TestCase):
    def setUp(self): self.task=json.loads(TASK_PATH.read_text(encoding="utf-8"))
    def test_baseline_submission_is_feasible(self):
        result=evaluate_case(self.task, solve_case(self.task)); self.assertTrue(result["feasible"], result)
    def test_wrong_primary_answer_is_rejected(self):
        submission=solve_case(self.task); submission['online_units']=['g2']; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("online_units" in v for v in result["violations"]), result)
    def test_wrong_summary_value_is_rejected(self):
        submission=solve_case(self.task); submission['short_circuit_ratio'] += 0.1; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("short_circuit_ratio" in v for v in result["violations"]), result)
    def test_unknown_field_is_rejected(self):
        submission=solve_case(self.task); submission["answer"]="leak"; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))
    def test_online_units_order_independent(self):
        submission=solve_case(self.task); submission["online_units"]=list(reversed(submission["online_units"])); result=evaluate_case(self.task, submission); self.assertTrue(result["feasible"], result)
if __name__=="__main__": unittest.main()
