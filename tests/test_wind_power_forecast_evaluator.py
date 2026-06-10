import json
import unittest
from pathlib import Path

from baselines.wind_power_forecast.baseline import solve_case
from prototype.evaluators.evaluate_wind_power_forecast import evaluate_case


ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "tasks/wind_power_forecast/public/case_001/task.json"


class WindPowerForecastEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = json.loads(TASK_PATH.read_text(encoding="utf-8"))

    def test_baseline_submission_is_feasible(self) -> None:
        result = evaluate_case(self.task, solve_case(self.task))
        self.assertTrue(result["feasible"], result)

    def test_wrong_timestamp_forecast_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["forecast_mw_by_timestamp"]["t02"] += 1.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("t02" in v for v in result["violations"]))

    def test_wrong_total_energy_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["total_forecast_mwh"] += 2.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("total_forecast_mwh" in v for v in result["violations"]))

    def test_wrong_peak_timestamp_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["peak_timestamp"] = "t01"
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("peak_timestamp" in v for v in result["violations"]))


if __name__ == "__main__":
    unittest.main()
