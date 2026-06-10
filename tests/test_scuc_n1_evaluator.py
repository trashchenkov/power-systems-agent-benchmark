import json
import unittest
from pathlib import Path
from baselines.scuc_n1.baseline import solve_case
from prototype.evaluators.evaluate_scuc_n1 import evaluate_case
ROOT=Path(__file__).resolve().parents[1]
TASK_PATH=ROOT/"tasks/scuc_n1/public/case_001/task.json"
class SCUCN1Tests(unittest.TestCase):
    def setUp(self): self.task=json.loads(TASK_PATH.read_text(encoding="utf-8"))
    def test_baseline_submission_is_feasible(self):
        result=evaluate_case(self.task, solve_case(self.task)); self.assertTrue(result["feasible"], result)
    def test_wrong_answer_is_rejected(self):
        submission=solve_case(self.task); submission['committed_units']=['g1','g2']; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("committed_units" in v for v in result["violations"]), result)
    def test_unknown_field_is_rejected(self):
        submission=solve_case(self.task); submission["answer"]="leak"; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))
if __name__=="__main__": unittest.main()
