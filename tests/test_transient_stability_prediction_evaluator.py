import json
import unittest
from pathlib import Path
from baselines.transient_stability_prediction.baseline import solve_case
from prototype.evaluators.evaluate_transient_stability_prediction import evaluate_case
ROOT=Path(__file__).resolve().parents[1]
TASK_PATH=ROOT/"tasks/transient_stability_prediction/public/case_001/task.json"
class TransientStabilityPredictionEvaluatorTests(unittest.TestCase):
    def setUp(self): self.task=json.loads(TASK_PATH.read_text(encoding="utf-8"))
    def test_baseline_submission_is_feasible(self):
        result=evaluate_case(self.task, solve_case(self.task)); self.assertTrue(result["feasible"], result)
    def test_wrong_primary_answer_is_rejected(self):
        submission=solve_case(self.task); submission['case_results']['fault_b']['label']='stable'; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("case_results.fault_b.label" in v for v in result["violations"]), result)
    def test_wrong_summary_value_is_rejected(self):
        submission=solve_case(self.task); submission['highest_risk_case']='fault_a'; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("highest_risk_case" in v for v in result["violations"]), result)
    def test_unknown_field_is_rejected(self):
        submission=solve_case(self.task); submission["answer"]="leak"; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))
if __name__=="__main__": unittest.main()
