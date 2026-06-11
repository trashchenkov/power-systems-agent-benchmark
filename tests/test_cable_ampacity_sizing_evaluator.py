import json
import math
import unittest
from pathlib import Path
from baselines.cable_ampacity_sizing.baseline import solve_case
from prototype.evaluators.evaluate_cable_ampacity_sizing import evaluate_case
ROOT=Path(__file__).resolve().parents[1]
TASK_PATH=ROOT/"tasks/cable_ampacity_sizing/public/case_001/task.json"
class CableAmpacitySizingEvaluatorTests(unittest.TestCase):
    def setUp(self): self.task=json.loads(TASK_PATH.read_text(encoding="utf-8"))
    def test_baseline_submission_is_feasible(self):
        result=evaluate_case(self.task, solve_case(self.task)); self.assertTrue(result["feasible"], result)
    def test_voltage_drop_governs_over_plain_ampacity(self):
        # 70 mm2 covers the design current after derating but breaks the 5 % drop limit,
        # so the smallest passing section must be 95 mm2.
        submission=solve_case(self.task)
        self.assertEqual(submission["selected_cross_section_mm2"], 95)
    def test_thermal_minimum_matches_adiabatic_formula(self):
        spec=self.task["cable_sizing_case"]; fault=spec["fault"]
        s_min=fault["fault_current_ka"]*1000*math.sqrt(fault["clearing_time_s"])/fault["k_adiabatic_a_sqrt_s_per_mm2"]
        submission=solve_case(self.task)
        self.assertAlmostEqual(submission["min_thermal_section_mm2"], s_min, places=4)
    def test_wrong_selection_is_rejected(self):
        submission=solve_case(self.task); submission["selected_cross_section_mm2"]=70
        result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"])
        self.assertTrue(any("selected_cross_section_mm2" in v for v in result["violations"]))
    def test_missing_field_and_unknown_key_are_rejected(self):
        submission=solve_case(self.task); del submission["selected_voltage_drop_pct"]; submission["answer"]="leak"
        result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"])
        self.assertTrue(any("selected_voltage_drop_pct" in v for v in result["violations"]))
        self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))
if __name__=="__main__": unittest.main()
