"""Malformed agent submissions must never crash an evaluator.

A submission that is structurally JSON but semantically garbage (nulls,
strings instead of numbers, empty objects, wrong shapes) is an agent failure
and must come back as feasible=False with violations — not as a Python
exception that kills a multi-case benchmark run. Found in the field: a
GigaChat-based agent returned nulls for every numeric field of
min_synchronous_share and the TypeError aborted the runner at 27/41 cases.
"""

import json
import unittest
from pathlib import Path

from scripts.evaluate_submission import EVALUATOR_MODULE_BY_FAMILY, evaluate_submission_file

ROOT = Path(__file__).resolve().parents[1]


def _public_paths(family):
    case_dir = ROOT / "tasks" / family / "public" / "case_001"
    return case_dir / "task.json", case_dir / "sample_submission.json"


def _malformed_variants(sample):
    nulled = {k: None for k in sample}
    strings = {k: "N/A" for k in sample}
    wrong_shapes = {k: ["unexpected"] for k in sample}
    return {
        "empty_object": {},
        "all_nulls": nulled,
        "all_strings": strings,
        "wrong_shapes": wrong_shapes,
    }


class MalformedSubmissionTests(unittest.TestCase):
    def test_no_evaluator_crashes_on_malformed_submissions(self):
        for family in sorted(EVALUATOR_MODULE_BY_FAMILY):
            task_path, sample_path = _public_paths(family)
            sample = json.loads(sample_path.read_text(encoding="utf-8"))
            for name, submission in _malformed_variants(sample).items():
                with self.subTest(family=family, variant=name):
                    tmp = ROOT / "runs" / ".tmp_malformed_submission.json"
                    tmp.write_text(json.dumps(submission), encoding="utf-8")
                    try:
                        result = evaluate_submission_file(task_path, tmp)
                    finally:
                        tmp.unlink(missing_ok=True)
                    self.assertFalse(result.get("feasible"), (family, name, result))
                    self.assertEqual(float(result.get("score", 1.0)), 0.0, (family, name))
                    self.assertTrue(result.get("violations"), (family, name))

    def test_min_synchronous_share_null_fields_reported_not_raised(self):
        # The exact field-shape from the original bug report.
        from prototype.evaluators.evaluate_min_synchronous_share import evaluate_case

        task = json.loads(_public_paths("min_synchronous_share")[0].read_text(encoding="utf-8"))
        submission = {
            "online_units": [],
            "min_synchronous_share_pct": None,
            "system_inertia_gws": None,
            "rocof_hz_per_s": None,
            "short_circuit_ratio": None,
        }
        result = evaluate_case(task, submission)
        self.assertFalse(result["feasible"])
        self.assertEqual(result["score"], 0.0)
        for key in ("min_synchronous_share_pct", "system_inertia_gws", "rocof_hz_per_s", "short_circuit_ratio"):
            self.assertTrue(any(key in v for v in result["violations"]), key)


if __name__ == "__main__":
    unittest.main()
