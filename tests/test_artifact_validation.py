import unittest

from scripts.validate_benchmark_artifacts import validate_task_data


class ArtifactValidationTests(unittest.TestCase):
    def valid_task(self):
        return {
            "task_id": "example_public_001",
            "family": "example",
            "substrate": "deterministic_surrogate",
            "objective": "Do the thing.",
            "bilingual": {
                "title": {"en": "Example task", "ru": "Пример задачи"},
                "objective": {"en": "Do the thing.", "ru": "Выполнить задачу."},
                "instructions": {"en": "Submit JSON.", "ru": "Отправьте JSON."},
            },
            "public_inputs": {},
            "submission_schema": {},
            "hard_constraints": ["Respect constraints."],
            "metrics": [
                {"name": "score", "direction": "maximize", "description": "Higher is better."}
            ],
            "source_evidence": ["Some source note"],
            "source_provenance": [
                {
                    "title": "Primary domain source",
                    "locator": "https://example.org/source or local path lines 1-2",
                    "confidence": "strong",
                    "notes": "Why this source supports the task.",
                }
            ],
        }

    def test_task_without_structured_source_provenance_is_rejected(self):
        task = self.valid_task()
        task.pop("source_provenance")

        errors = validate_task_data(task, "memory/task.json")

        self.assertIn("memory/task.json: missing required fields: ['source_provenance']", errors)

    def test_source_provenance_requires_title_locator_confidence_and_notes(self):
        task = self.valid_task()
        task["source_provenance"] = [{"title": "Only title"}]

        errors = validate_task_data(task, "memory/task.json")

        self.assertIn("memory/task.json: source_provenance[0] missing locator", errors)
        self.assertIn("memory/task.json: source_provenance[0] missing confidence", errors)
        self.assertIn("memory/task.json: source_provenance[0] missing notes", errors)

    def test_valid_structured_source_provenance_is_accepted(self):
        errors = validate_task_data(self.valid_task(), "memory/task.json")

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
