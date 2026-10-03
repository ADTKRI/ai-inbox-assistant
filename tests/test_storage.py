"""Unit tests for SQLite storage persistence service."""

from pathlib import Path
import sys
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from schemas import EmailTriageResult
from services.storage import (
    clear_all_triages,
    delete_triage,
    get_all_triages,
    init_db,
    save_triage,
)


def test_storage_lifecycle() -> None:
    """Test database initialization, insert, query, delete, and wipe operations."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_db = Path(tmp_dir) / "test_inbox.db"

        # 1. Initialize schema
        init_db(test_db)
        assert test_db.exists(), "Database file should exist after init_db"

        # 2. Save record
        dummy_result = EmailTriageResult(
            priority="HIGH",
            priority_reason="Urgent contract review",
            summary="Review and sign contract by tomorrow.",
            actions=["Download PDF", "Sign electronically"],
            deadline="2026-10-04",
            reply_required=True,
            reply_reason="Signature confirmation requested",
            category="WORK",
        )
        row_id = save_triage(
            subject="Urgent: Contract Signature",
            raw_text="Please sign the attached document by tomorrow.",
            result=dummy_result,
            db_path=test_db,
        )
        assert row_id == 1, f"Expected row ID 1, got {row_id}"

        # 3. Retrieve records
        records = get_all_triages(db_path=test_db)
        assert len(records) == 1, f"Expected 1 record, got {len(records)}"
        rec = records[0]
        assert rec["id"] == 1
        assert rec["subject"] == "Urgent: Contract Signature"
        assert rec["result"].priority == "HIGH"
        assert len(rec["result"].actions) == 2
        assert rec["result"].reply_required is True

        # 4. Save second record
        dummy_result_2 = EmailTriageResult(
            priority="LOW",
            priority_reason="Newsletter broadcast",
            summary="Weekly engineering update.",
            actions=[],
            deadline=None,
            reply_required=False,
            reply_reason=None,
            category="NEWSLETTER",
        )
        row_id_2 = save_triage(
            subject="Engineering Weekly #22",
            raw_text="Here is your weekly update.",
            result=dummy_result_2,
            db_path=test_db,
        )
        assert row_id_2 == 2

        # Verify ordering (newest first)
        records = get_all_triages(db_path=test_db)
        assert len(records) == 2
        assert records[0]["id"] == 2
        assert records[1]["id"] == 1

        # 5. Delete individual record
        del_success = delete_triage(1, db_path=test_db)
        assert del_success is True
        records_after_del = get_all_triages(db_path=test_db)
        assert len(records_after_del) == 1
        assert records_after_del[0]["id"] == 2

        # 6. Clear all
        clear_success = clear_all_triages(db_path=test_db)
        assert clear_success is True
        assert len(get_all_triages(db_path=test_db)) == 0

        print("All storage lifecycle tests passed successfully!")


if __name__ == "__main__":
    test_storage_lifecycle()
