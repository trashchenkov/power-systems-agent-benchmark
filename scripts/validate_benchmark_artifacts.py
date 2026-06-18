"""Smoke validation for benchmark v0 artifacts.

Uses only the Python standard library so it can run before benchmark runtime
dependencies such as pandapower are installed.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_TASK_FIELDS = {
    "task_id",
    "family",
    "substrate",
    "objective",
    "public_inputs",
    "submission_schema",
    "hard_constraints",
    "metrics",
    "source_evidence",
    "source_provenance",
}

REQUIRED_SOURCE_PROVENANCE_FIELDS = {"title", "locator", "confidence", "notes"}
REQUIRED_BILINGUAL_FIELDS = {"title", "objective", "instructions"}

REQUIRED_REPO_FILES = [
    "README.md",
    "LICENSE",
    "benchmark_spec_v0.md",
    "docs/evaluator_contract.md",
    "docs/public_hidden_split.md",
    "docs/metrics.md",
    "schemas/task.schema.json",
    "schemas/submission.schema.json",
    "schemas/evaluation-result.schema.json",
    "scripts/check.sh",
]


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_task_data(data: dict, path_label: str) -> list[str]:
    """Validate one task artifact already loaded as JSON-compatible data."""
    errors: list[str] = []
    missing = sorted(REQUIRED_TASK_FIELDS - set(data))
    if missing:
        errors.append(f"{path_label}: missing required fields: {missing}")
    if not isinstance(data.get("metrics"), list) or not data.get("metrics"):
        errors.append(f"{path_label}: metrics must be a non-empty list")
    for idx, metric in enumerate(data.get("metrics", [])):
        for key in ("name", "direction", "description"):
            if key not in metric:
                errors.append(f"{path_label}: metrics[{idx}] missing {key}")

    source_provenance = data.get("source_provenance")
    if source_provenance is not None:
        if not isinstance(source_provenance, list) or not source_provenance:
            errors.append(f"{path_label}: source_provenance must be a non-empty list")
        else:
            for idx, source in enumerate(source_provenance):
                if not isinstance(source, dict):
                    errors.append(f"{path_label}: source_provenance[{idx}] must be an object")
                    continue
                for key in sorted(REQUIRED_SOURCE_PROVENANCE_FIELDS):
                    if key not in source:
                        errors.append(f"{path_label}: source_provenance[{idx}] missing {key}")
                    elif not str(source[key]).strip():
                        errors.append(f"{path_label}: source_provenance[{idx}].{key} must be non-empty")

    public_inputs = data.get("public_inputs")
    if isinstance(public_inputs, dict):
        # Several families mirror case data both inside public_inputs and at the
        # top level; evaluators read one copy and agents may read the other, so
        # the copies must never drift apart.
        for key, value in public_inputs.items():
            if key in data and data[key] != value:
                errors.append(f"{path_label}: public_inputs.{key} diverged from the top-level copy")

    bilingual = data.get("bilingual")
    if not isinstance(bilingual, dict):
        errors.append(f"{path_label}: bilingual must be an object with English and Russian text")
    else:
        for field in sorted(REQUIRED_BILINGUAL_FIELDS):
            value = bilingual.get(field)
            if not isinstance(value, dict):
                errors.append(f"{path_label}: bilingual.{field} must be an object")
                continue
            for lang in ("en", "ru"):
                if not str(value.get(lang, "")).strip():
                    errors.append(f"{path_label}: bilingual.{field}.{lang} must be non-empty")
    return errors


def validate_task(path: Path) -> list[str]:
    data = load_json(path)
    errors = validate_task_data(data, str(path))
    if data.get("task_id") and path.parent.name.startswith("case_") is False:
        errors.append(f"{path}: expected to live under case_* directory")
    return errors


def main() -> int:
    task_paths = sorted(ROOT.glob("tasks/*/*/case_*/task.json"))
    errors: list[str] = []

    if not task_paths:
        errors.append("no task.json files found")

    for required_path in REQUIRED_REPO_FILES:
        if not (ROOT / required_path).exists():
            errors.append(f"missing required repo file: {required_path}")

    for schema_path in sorted((ROOT / "schemas").glob("*.json")):
        try:
            load_json(schema_path)
        except json.JSONDecodeError as exc:
            errors.append(f"{schema_path}: invalid JSON schema file: {exc}")

    for task_path in task_paths:
        errors.extend(validate_task(task_path))

    if errors:
        print("Artifact validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"OK: validated {len(task_paths)} task artifact(s), "
        f"{len(REQUIRED_REPO_FILES)} required repo file(s), "
        f"and {len(list((ROOT / 'schemas').glob('*.json')))} schema file(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
