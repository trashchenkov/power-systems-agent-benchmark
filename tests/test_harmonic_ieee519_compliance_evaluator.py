import json
import math
import unittest
from pathlib import Path
from baselines.harmonic_ieee519_compliance.baseline import solve_case
from prototype.evaluators.evaluate_harmonic_ieee519_compliance import evaluate_case
ROOT=Path(__file__).resolve().parents[1]
TASK_PATH=ROOT/"tasks/harmonic_ieee519_compliance/public/case_001/task.json"
class HarmonicIeee519ComplianceEvaluatorTests(unittest.TestCase):
    def setUp(self): self.task=json.loads(TASK_PATH.read_text(encoding="utf-8"))
    def test_baseline_submission_is_feasible(self):
        result=evaluate_case(self.task, solve_case(self.task)); self.assertTrue(result["feasible"], result)
    def test_tdd_uses_max_demand_current_not_measured_fundamental(self):
        spec=self.task["harmonic_case"]
        il=spec["pcc"]["max_demand_current_a"]
        tdd=math.sqrt(sum(v*v for v in spec["measured"]["harmonic_currents_a"].values()))/il*100
        submission=solve_case(self.task)
        self.assertAlmostEqual(submission["tdd_pct"], tdd, places=4)
        self.assertNotAlmostEqual(
            submission["tdd_pct"],
            tdd*il/spec["measured"]["fundamental_current_a"],
            places=2,
        )
    def test_wrong_ratio_is_rejected(self):
        submission=solve_case(self.task); submission["isc_over_il"] += 1.0
        result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"])
        self.assertTrue(any("isc_over_il" in v for v in result["violations"]))
    def test_wrong_violation_list_is_rejected(self):
        submission=solve_case(self.task); submission["current_violations"]=["5"]
        result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"])
        self.assertTrue(any("current_violations" in v for v in result["violations"]))
    def test_wrong_verdict_and_unknown_key_are_rejected(self):
        submission=solve_case(self.task); submission["compliant"]=not submission["compliant"]; submission["answer"]="leak"
        result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"])
        self.assertTrue(any("compliant" in v for v in result["violations"]))
        self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))
if __name__=="__main__": unittest.main()
