import json
import unittest
from pathlib import Path
from baselines.ibr_short_circuit_frt.baseline import solve_case
from prototype.evaluators.evaluate_ibr_short_circuit_frt import evaluate_case
ROOT=Path(__file__).resolve().parents[1]
TASK_PATH=ROOT/"tasks/ibr_short_circuit_frt/public/case_001/task.json"
class IBRShortCircuitFRTEvaluatorTests(unittest.TestCase):
    def setUp(self): self.task=json.loads(TASK_PATH.read_text(encoding="utf-8"))
    def test_baseline_submission_is_feasible(self):
        result=evaluate_case(self.task, solve_case(self.task)); self.assertTrue(result["feasible"], result)
    def test_wrong_primary_answer_is_rejected(self):
        submission=solve_case(self.task); submission['current_profile_pu']['t160']['iq_pu'] -= 0.05; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("current_profile_pu.t160.iq_pu" in v for v in result["violations"]), result)
    def test_wrong_summary_value_is_rejected(self):
        submission=solve_case(self.task); submission['frt_compliant']=False; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("frt_compliant" in v for v in result["violations"]), result)
    def test_unknown_field_is_rejected(self):
        submission=solve_case(self.task); submission["answer"]="leak"; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))
if __name__=="__main__": unittest.main()
