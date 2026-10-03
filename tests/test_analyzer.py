"""Standalone verification test for EmailAnalyzer service using benchmark email."""

import json
from pathlib import Path
import sys

# Ensure project root is available in module search path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.analyzer import EmailAnalyzer


def test_analyze_benchmark_email() -> None:
    """Verify EmailAnalyzer extracts correct metadata from the onboarding benchmark email."""
    subject = "Internship Onboarding - Document Submission"
    raw_text = (
        "Please submit your updated resume and offer letter by September 28. "
        "Also confirm once the documents have been uploaded."
    )

    print("Initializing EmailAnalyzer...")
    analyzer = EmailAnalyzer()

    print(f"Analyzing benchmark email:\n  Subject: {subject}\n  Body: {raw_text}\n")
    result = analyzer.analyze_email(raw_text=raw_text, subject=subject)

    print("=== Triage Result (JSON) ===")
    print(json.dumps(result.model_dump(), indent=2))
    print("============================\n")

    # 1. Assert and print priority
    print(f"[*] Priority: {result.priority}")
    assert result.priority == "HIGH", f"Expected 'HIGH', got {result.priority}"

    # 2. Assert and print actions
    print(f"[*] Actions: {result.actions}")
    assert isinstance(result.actions, list) and len(result.actions) > 0, "Expected non-empty actions list"
    actions_text = " ".join(result.actions).lower()
    assert any(
        kw in actions_text for kw in ("resume", "offer", "upload", "submit", "document")
    ), f"Actions should mention file upload or submission: {result.actions}"

    # 3. Assert and print deadline
    print(f"[*] Deadline: {result.deadline}")
    assert result.deadline is not None, "Expected deadline to be detected"
    assert any(
        kw in result.deadline.lower() for kw in ("september 28", "09-28", "28")
    ), f"Deadline should detect September 28: {result.deadline}"

    # 4. Assert and print reply_required
    print(f"[*] Reply Required: {result.reply_required} (Reason: {result.reply_reason})")
    assert result.reply_required is True, "Expected reply_required to be True"

    # 5. Assert and print category
    print(f"[*] Category: {result.category}")
    assert result.category in ("INTERNSHIP", "WORK"), (
        f"Expected category 'INTERNSHIP' or 'WORK', got {result.category}"
    )

    # 6. Verify empty raw_text raises ValueError
    print("\n[*] Testing empty raw_text error handling...")
    try:
        analyzer.analyze_email(raw_text="   ", subject="Empty")
        assert False, "Expected ValueError on empty email text"
    except ValueError:
        print("  -> Correctly raised ValueError on empty raw_text.")

    print("\nAll benchmark email triage assertions passed successfully!")


if __name__ == "__main__":
    try:
        test_analyze_benchmark_email()
    except Exception as exc:
        print(f"\nVerification test failed: {exc}", file=sys.stderr)
        sys.exit(1)
