import json
import unittest
from pathlib import Path

from baselines.microgrid_economic_dispatch.baseline import solve_case
from prototype.evaluators.evaluate_microgrid_economic_dispatch import evaluate_case

ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "tasks/microgrid_economic_dispatch/public/case_001/task.json"


class MicrogridEconomicDispatchEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = json.loads(TASK_PATH.read_text(encoding="utf-8"))

    def test_baseline_submission_is_feasible(self) -> None:
        result = evaluate_case(self.task, solve_case(self.task))
        self.assertTrue(result["feasible"], result)

    def test_wrong_dispatch_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission['dispatch'][next(iter(submission['dispatch']))]['diesel_mw'] += 1.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("diesel_mw" in v for v in result["violations"]))

    def test_wrong_total_or_voltage_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission['total_cost'] += 100.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("total_cost" in v for v in result["violations"]))

    def test_unknown_field_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["answer"] = "leak"
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))


    def test_equal_cost_alternative_optimum_is_accepted(self) -> None:
        import itertools
        from prototype.evaluators.evaluate_microgrid_economic_dispatch import _simulate, _times, solve_core, CASE_KEY
        case = self.task[CASE_KEY]
        exp = solve_core(self.task)
        b = case["battery"]; step = float(b["dispatch_step_mw"])
        vals = []; x = -float(b["charge_pmax_mw"])
        while x <= float(b["discharge_pmax_mw"]) + 1e-9:
            vals.append(round(x, 6)); x += step
        alternative = None
        for combo in itertools.product(vals, repeat=len(_times(case))):
            feas, cost, rows = _simulate(case, combo)
            if feas and abs(cost - exp["total_cost"]) < 1e-6 and rows != exp["dispatch"]:
                alternative = (cost, rows); break
        if alternative is None:
            self.skipTest("no equal-cost alternative optimum in this public case")
        cost, rows = alternative
        result = evaluate_case(self.task, {"dispatch": rows, "total_cost": cost})
        self.assertTrue(result["feasible"], result)
        self.assertEqual(result["score"], 1.0)
        self.assertEqual(result["cost_gap_usd"], 0.0)

    def test_suboptimal_feasible_dispatch_gets_partial_credit(self) -> None:
        import itertools
        from prototype.evaluators.evaluate_microgrid_economic_dispatch import _simulate, _times, solve_core, CASE_KEY
        case = self.task[CASE_KEY]
        exp = solve_core(self.task)
        b = case["battery"]; step = float(b["dispatch_step_mw"])
        vals = []; x = -float(b["charge_pmax_mw"])
        while x <= float(b["discharge_pmax_mw"]) + 1e-9:
            vals.append(round(x, 6)); x += step
        suboptimal = None
        for combo in itertools.product(vals, repeat=len(_times(case))):
            feas, cost, rows = _simulate(case, combo)
            if feas and cost > exp["total_cost"] + 1.0:
                suboptimal = (cost, rows); break
        self.assertIsNotNone(suboptimal)
        cost, rows = suboptimal
        result = evaluate_case(self.task, {"dispatch": rows, "total_cost": cost})
        self.assertTrue(result["feasible"], result)
        self.assertLess(result["score"], 1.0)
        self.assertGreater(result["score"], 0.0)
        self.assertGreater(result["cost_gap_usd"], 0.0)

    def test_soc_violating_schedule_is_rejected(self) -> None:
        from prototype.evaluators.evaluate_microgrid_economic_dispatch import _simulate, _times, CASE_KEY
        case = self.task[CASE_KEY]
        battery = [float(case["battery"]["discharge_pmax_mw"])] * len(_times(case))
        feas, cost, rows = _simulate(case, battery)
        if feas:
            self.skipTest("max discharge stays within SOC for this public case")
        result = evaluate_case(self.task, {"dispatch": rows, "total_cost": cost})
        self.assertFalse(result["feasible"])
        self.assertTrue(any("SOC bounds or sheds load" in v for v in result["violations"]))

if __name__ == "__main__":
    unittest.main()
