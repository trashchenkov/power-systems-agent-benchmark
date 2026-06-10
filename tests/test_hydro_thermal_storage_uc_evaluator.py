import json
import unittest
from pathlib import Path
from baselines.hydro_thermal_storage_uc.baseline import solve_case
from prototype.evaluators.evaluate_hydro_thermal_storage_uc import evaluate_case
ROOT=Path(__file__).resolve().parents[1]
TASK_PATH=ROOT/"tasks/hydro_thermal_storage_uc/public/case_001/task.json"
class HydroThermalStorageUCTests(unittest.TestCase):
    def setUp(self): self.task=json.loads(TASK_PATH.read_text(encoding="utf-8"))
    def test_baseline_submission_is_feasible(self):
        result=evaluate_case(self.task, solve_case(self.task)); self.assertTrue(result["feasible"], result)
    def test_wrong_answer_is_rejected(self):
        submission=solve_case(self.task); submission['total_cost_usd'] += 1; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("total_cost_usd" in v for v in result["violations"]), result)
    def test_unknown_field_is_rejected(self):
        submission=solve_case(self.task); submission["answer"]="leak"; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))
if __name__=="__main__": unittest.main()
