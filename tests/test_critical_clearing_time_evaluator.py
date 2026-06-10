import json
import math
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
    def test_equal_area_values_match_independent_hand_calculation(self):
        spec=self.task["public_inputs"]["smib_cct_case"]
        pm=spec["mechanical_power_pu"]; p_pre=spec["prefault_pmax_pu"]; p_post=spec["postfault_pmax_pu"]
        delta0=math.asin(pm/p_pre); delta_max=math.pi-math.asin(pm/p_post)
        cos_dcr=(pm*(delta_max-delta0)+p_post*math.cos(delta_max))/p_post
        delta_cr=math.acos(cos_dcr)
        t_cr=math.sqrt(4*spec["inertia_h_s"]*(delta_cr-delta0)/(2*math.pi*spec["nominal_frequency_hz"]*pm))
        submission=solve_case(self.task)
        self.assertAlmostEqual(submission["delta_critical_deg"], math.degrees(delta_cr), places=4)
        self.assertAlmostEqual(submission["critical_clearing_time_s"], t_cr, places=5)
    def test_wrong_clearing_time_is_rejected(self):
        submission=solve_case(self.task); submission['critical_clearing_time_s'] += 0.01; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("critical_clearing_time_s" in v for v in result["violations"]), result)
    def test_wrong_critical_angle_is_rejected(self):
        submission=solve_case(self.task); submission['delta_critical_deg'] += 0.5; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("delta_critical_deg" in v for v in result["violations"]), result)
    def test_missing_field_is_rejected(self):
        submission=solve_case(self.task); del submission['delta_max_deg']; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("delta_max_deg" in v for v in result["violations"]), result)
    def test_unknown_field_is_rejected(self):
        submission=solve_case(self.task); submission["answer"]="leak"; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))
if __name__=="__main__": unittest.main()
