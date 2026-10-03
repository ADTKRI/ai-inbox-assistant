"""Standalone test script and verification for EmailTriageResult schema."""

import json
from pathlib import Path
import sys

# Ensure project root is available in module search path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from schemas import EmailTriageResult


def test_email_triage_result_valid() -> None:
    """Validate model instantiation, field values, and schema generation."""
    dummy_data = {
        "priority": "HIGH",
        "priority_reason": "Upcoming final-round interview scheduling request within 24 hours.",
        "summary": "Technical recruiter reached out to schedule a 45-minute technical screen for the Summer 2027 Software Engineering Internship.",
        "actions": [
            "Confirm availability for Thursday or Friday slots",
            "Update portfolio link and resume copy",
        ],
        "deadline": "2026-10-05T17:00:00Z",
        "reply_required": True,
        "reply_reason": "Recruiter requested preferred interview slots to confirm calendar invitation.",
        "category": "INTERNSHIP",
    }

    # Instantiate and validate through Pydantic
    triage_result = EmailTriageResult(**dummy_data)

    # Basic runtime validation assertions
    assert triage_result.priority == "HIGH"
    assert triage_result.category == "INTERNSHIP"
    assert triage_result.reply_required is True
    assert len(triage_result.actions) == 2
    assert triage_result.deadline == "2026-10-05T17:00:00Z"

    print("=== Successfully Validated EmailTriageResult Instance ===")
    print(json.dumps(triage_result.model_dump(), indent=2))

    print("\n=== EmailTriageResult JSON Schema ===")
    schema = EmailTriageResult.model_json_schema()
    print(json.dumps(schema, indent=2))


if __name__ == "__main__":
    try:
        test_email_triage_result_valid()
        print("\nAll schema validations passed successfully.")
    except Exception as exc:
        print(f"\nSchema validation failed: {exc}", file=sys.stderr)
        sys.exit(1)
