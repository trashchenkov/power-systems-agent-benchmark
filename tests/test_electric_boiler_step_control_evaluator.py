import json
import unittest
from pathlib import Path
from baselines.electric_boiler_step_control.baseline import solve_case
from prototype.evaluators.evaluate_electric_boiler_step_control import evaluate_case
ROOT=Path(__file__).resolve().parents[1]
TASK_PATH=ROOT/"tasks/electric_boiler_step_control/public/case_001/task.json"
class ElectricBoilerStepControlEvaluatorTests(unittest.TestCase):
    def setUp(self): self.task=json.loads(TASK_PATH.read_text(encoding="utf-8"))
    def test_baseline_submission_is_feasible(self):
        result=evaluate_case(self.task, solve_case(self.task)); self.assertTrue(result["feasible"], result)
    def test_wrong_primary_answer_is_rejected(self):
        submission=solve_case(self.task); submission['control_steps']['t30']['stage_kw'] -= 25; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("control_steps.t30.stage_kw" in v for v in result["violations"]))
    def test_wrong_summary_value_is_rejected(self):
        submission=solve_case(self.task); submission['total_energy_kwh'] += 1; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("total_energy" in v for v in result["violations"]))
    def test_unknown_field_is_rejected(self):
        submission=solve_case(self.task); submission["answer"]="leak"; result=evaluate_case(self.task, submission); self.assertFalse(result["feasible"]); self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))
if __name__=="__main__": unittest.main()
