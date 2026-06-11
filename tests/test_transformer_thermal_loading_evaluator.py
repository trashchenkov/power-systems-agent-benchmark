import json
import math
import unittest
from pathlib import Path
from baselines.transformer_thermal_loading.baseline import solve_case
from prototype.evaluators.evaluate_transformer_thermal_loading import evaluate_case
ROOT=Path(__file__).resolve().parents[1]
TASK_PATH=ROOT/"tasks/transformer_thermal_loading/public/case_001/task.json"
class TransformerThermalLoadingEvaluatorTests(unittest.TestCase):
    def setUp(self): self.task=json.loads(TASK_PATH.read_text(encoding="utf-8"))
    def test_baseline_submission_is_feasible(self):
        result=evaluate_case(self.task, solve_case(self.task)); self.assertTrue(result["feasible"], result)
    def test_first_step_matches_hand_calculation(self):
        spec=self.task["transformer_thermal_case"]; rated=spec["rated"]; step=spec["load_steps"][0]
        k=step["load_factor_pu"]
        target=rated["top_oil_rise_rated_k"]*(((1+rated["loss_ratio_r"]*k*k)/(1+rated["loss_ratio_r"]))**rated["oil_exponent_x"])
        rise=target+(spec["initial_top_oil_rise_k"]-target)*math.exp(-step["duration_h"]/rated["oil_time_constant_h"])
        hs=step["ambient_c"]+rise+rated["hot_spot_gradient_rated_k"]*(k**rated["winding_exponent_y"])
        submission=solve_case(self.task)
        self.assertAlmostEqual(submission["hot_spot_c"]["s1"], hs, places=4)
    def test_hot_spot_error_is_rejected(self):
        submission=solve_case(self.task); submission["hot_spot_c"]["s2"] += 1.0
        result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"])
        self.assertTrue(any("hot_spot_c.s2" in v for v in result["violations"]))
    def test_wrong_admissibility_verdict_is_rejected(self):
        submission=solve_case(self.task); submission["overload_admissible"]=not submission["overload_admissible"]
        result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"])
        self.assertTrue(any("overload_admissible" in v for v in result["violations"]))
    def test_missing_step_and_unknown_field_are_rejected(self):
        submission=solve_case(self.task); del submission["ageing_rate"]["s3"]; submission["answer"]="leak"
        result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"])
        self.assertTrue(any("ageing_rate missing step s3" in v for v in result["violations"]))
        self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))
if __name__=="__main__": unittest.main()
