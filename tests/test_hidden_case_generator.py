import json
import unittest
from pathlib import Path

from scripts.evaluate_submission import EVALUATOR_MODULE_BY_FAMILY
from scripts.generate_hidden_cases import GENERATORS, generate_case

ROOT = Path(__file__).resolve().parents[1]
SEED = "unit-test-seed"


class HiddenCaseGeneratorTests(unittest.TestCase):
    def test_every_evaluator_family_has_a_generator(self):
        self.assertEqual(sorted(GENERATORS), sorted(EVALUATOR_MODULE_BY_FAMILY))

    def test_generates_feasible_cases_distinct_from_public_for_all_families(self):
        for family in sorted(GENERATORS):
            with self.subTest(family=family):
                task = generate_case(ROOT, family, SEED, "902")
                self.assertEqual(task["task_id"], f"{family}_hidden_902")
                public = json.loads(
                    (ROOT / "tasks" / family / "public" / "case_001" / "task.json").read_text(encoding="utf-8")
                )
                task_body = {k: v for k, v in task.items() if k != "task_id"}
                public_body = {k: v for k, v in public.items() if k != "task_id"}
                self.assertNotEqual(task_body, public_body, "hidden case must differ from the public case")

    def test_generation_is_deterministic_in_seed_and_sensitive_to_it(self):
        family = "three_phase_short_circuit"
        first = generate_case(ROOT, family, SEED, "903")
        second = generate_case(ROOT, family, SEED, "903")
        other_seed = generate_case(ROOT, family, "another-seed", "903")
        self.assertEqual(first, second)
        self.assertNotEqual(first, other_seed)

    def test_public_inputs_mirror_stays_in_sync_with_top_level_copies(self):
        for family in sorted(GENERATORS):
            with self.subTest(family=family):
                task = generate_case(ROOT, family, SEED, "904")
                inputs = task.get("public_inputs", {})
                for key, value in inputs.items():
                    if key in task:
                        self.assertEqual(task[key], value, f"{family}: public_inputs.{key} diverged from top-level copy")


if __name__ == "__main__":
    unittest.main()
