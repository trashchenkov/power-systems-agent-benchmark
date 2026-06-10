import json
import unittest
from pathlib import Path
from baselines.protected_meter_placement.baseline import solve_case
from prototype.evaluators.evaluate_protected_meter_placement import evaluate_case
ROOT=Path(__file__).resolve().parents[1]
TASK_PATH=ROOT/"tasks/protected_meter_placement/public/case_001/task.json"
class ProtectedMeterPlacementTests(unittest.TestCase):
    def setUp(self): self.task=json.loads(TASK_PATH.read_text(encoding="utf-8"))
    def test_baseline_submission_is_feasible(self):
        result=evaluate_case(self.task, solve_case(self.task)); self.assertTrue(result["feasible"], result)
    def test_wrong_answer_is_rejected(self):
        submission=solve_case(self.task); submission['protected_meters']=['m12','m23']; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("protected_meters" in v for v in result["violations"]), result)
    def test_unknown_field_is_rejected(self):
        submission=solve_case(self.task); submission["answer"]="leak"; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))
if __name__=="__main__": unittest.main()
