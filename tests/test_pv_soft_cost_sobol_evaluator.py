import json
import unittest
from pathlib import Path
from baselines.pv_soft_cost_sobol.baseline import solve_case
from prototype.evaluators.evaluate_pv_soft_cost_sobol import evaluate_case
ROOT=Path(__file__).resolve().parents[1]
TASK_PATH=ROOT/"tasks/pv_soft_cost_sobol/public/case_001/task.json"
class PVSoftCostSobolEvaluatorTests(unittest.TestCase):
    def setUp(self): self.task=json.loads(TASK_PATH.read_text(encoding="utf-8"))
    def test_baseline_submission_is_feasible(self):
        result=evaluate_case(self.task, solve_case(self.task)); self.assertTrue(result["feasible"], result)
    def test_wrong_primary_answer_is_rejected(self):
        submission=solve_case(self.task); submission['sensitivity_ranking'] = list(reversed(submission['sensitivity_ranking'])); result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("sensitivity_ranking" in v for v in result["violations"]))
    def test_wrong_summary_value_is_rejected(self):
        submission=solve_case(self.task); submission['first_order_indices']['interconnection'] += 0.1; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("first_order_indices.interconnection" in v for v in result["violations"]))
    def test_unknown_field_is_rejected(self):
        submission=solve_case(self.task); submission["answer"]="leak"; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))
if __name__=="__main__": unittest.main()
