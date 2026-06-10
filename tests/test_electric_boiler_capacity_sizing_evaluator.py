import json
import unittest
from pathlib import Path
from baselines.electric_boiler_capacity_sizing.baseline import solve_case
from prototype.evaluators.evaluate_electric_boiler_capacity_sizing import evaluate_case
ROOT=Path(__file__).resolve().parents[1]
TASK_PATH=ROOT/"tasks/electric_boiler_capacity_sizing/public/case_001/task.json"
class ElectricBoilerCapacitySizingEvaluatorTests(unittest.TestCase):
    def setUp(self): self.task=json.loads(TASK_PATH.read_text(encoding="utf-8"))
    def test_baseline_submission_is_feasible(self):
        result=evaluate_case(self.task, solve_case(self.task)); self.assertTrue(result["feasible"], result)
    def test_wrong_primary_answer_is_rejected(self):
        submission=solve_case(self.task); submission['capacity_kw'] += 5; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("capacity_kw" in v for v in result["violations"]))
    def test_wrong_summary_value_is_rejected(self):
        submission=solve_case(self.task); submission['peak_residual_heat_kw_th'] += 1; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("peak_residual" in v for v in result["violations"]))
    def test_unknown_field_is_rejected(self):
        submission=solve_case(self.task); submission["answer"]="leak"; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))
if __name__=="__main__": unittest.main()
