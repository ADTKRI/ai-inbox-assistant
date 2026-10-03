"""SQLite persistence service for email triage records."""

from contextlib import contextmanager
import datetime
import json
from pathlib import Path
import sqlite3
from typing import Any, Generator

from schemas import EmailTriageResult

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "inbox_history.db"


@contextmanager
def get_db_connection(db_path: Path) -> Generator[sqlite3.Connection, None, None]:
    """Context manager for SQLite database connections that ensures closure.

    Args:
        db_path: Path to the SQLite database file.

    Yields:
        sqlite3.Connection: Active database connection.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Ensure data directory and database schema exist safely.

    Args:
        db_path: File system path to the SQLite database.
    """
    with get_db_connection(db_path) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS triage_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    subject TEXT,
                    original_text TEXT,
                    priority TEXT,
                    priority_reason TEXT,
                    summary TEXT,
                    actions_json TEXT,
                    deadline TEXT,
                    reply_required INTEGER,
                    reply_reason TEXT,
                    category TEXT
                );
                """
            )


def save_triage(
    subject: str,
    raw_text: str,
    result: EmailTriageResult,
    db_path: Path = DEFAULT_DB_PATH,
) -> int:
    """Persist an email triage result to SQLite.

    Args:
        subject: Email subject line.
        raw_text: Full original email text body.
        result: Validated EmailTriageResult Pydantic model.
        db_path: SQLite database file path.

    Returns:
        int: The primary key ID of the newly inserted row.
    """
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO triage_history (
                    subject, original_text, priority, priority_reason, summary,
                    actions_json, deadline, reply_required, reply_reason, category
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    subject,
                    raw_text,
                    result.priority,
                    result.priority_reason,
                    result.summary,
                    json.dumps(result.actions),
                    result.deadline,
                    1 if result.reply_required else 0,
                    result.reply_reason,
                    result.category,
                ),
            )
            return int(cursor.lastrowid)


def get_all_triages(limit: int = 50, db_path: Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    """Retrieve stored email triage records in reverse chronological order.

    Args:
        limit: Maximum number of records to retrieve.
        db_path: SQLite database file path.

    Returns:
        list[dict]: List of record dictionaries ready for session state and UI display.
    """
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, created_at, subject, original_text, priority, priority_reason,
                   summary, actions_json, deadline, reply_required, reply_reason, category
            FROM triage_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()

    records = []
    for row in rows:
        try:
            actions = json.loads(row["actions_json"]) if row["actions_json"] else []
        except Exception:
            actions = []

        result_model = EmailTriageResult(
            priority=row["priority"],
            priority_reason=row["priority_reason"],
            summary=row["summary"],
            actions=actions,
            deadline=row["deadline"],
            reply_required=bool(row["reply_required"]),
            reply_reason=row["reply_reason"],
            category=row["category"],
        )

        created_str = row["created_at"] or ""
        time_display = ""
        if created_str:
            try:
                dt = datetime.datetime.strptime(created_str, "%Y-%m-%d %H:%M:%S")
                time_display = dt.strftime("%I:%M %p")
            except Exception:
                time_display = created_str[11:16] if len(created_str) >= 16 else created_str

        records.append(
            {
                "id": row["id"],
                "subject": row["subject"] or "Untitled Email",
                "body": row["original_text"] or "",
                "result": result_model,
                "timestamp": time_display,
                "actions_completed": {i: False for i in range(len(actions))},
            }
        )

    return records


def delete_triage(triage_id: int, db_path: Path = DEFAULT_DB_PATH) -> bool:
    """Delete a single triage record by its ID.

    Args:
        triage_id: Primary key of the record to delete.
        db_path: SQLite database file path.

    Returns:
        bool: True if row was deleted, False otherwise.
    """
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM triage_history WHERE id = ?", (triage_id,))
            return cursor.rowcount > 0


def clear_all_triages(db_path: Path = DEFAULT_DB_PATH) -> bool:
    """Delete all records from the triage history database.

    Args:
        db_path: SQLite database file path.

    Returns:
        bool: True upon completion.
    """
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM triage_history")
            return True
