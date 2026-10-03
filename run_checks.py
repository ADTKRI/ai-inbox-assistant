"""Production diagnostic and automated health check script for AI Inbox Assistant.

Validates:
1. Environment & API key presence (.env).
2. SQLite local database initialization, table schema, and write permissions.
3. Pydantic v2 EmailTriageResult schema constraints and serialization.
4. Live Gemini API network connectivity and latency.
"""

from datetime import datetime
import json
import os
from pathlib import Path
import sqlite3
import sys
import time

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from schemas import EmailTriageResult
from services.storage import DEFAULT_DB_PATH, get_db_connection, init_db


class HealthChecker:
    """Unified system health checker for production readiness verification."""

    def __init__(self) -> None:
        self.results: list[dict[str, str]] = []
        self.all_passed = True

    def log_result(self, name: str, status: str, details: str) -> None:
        """Record check result."""
        self.results.append({"name": name, "status": status, "details": details})
        if status != "PASS":
            self.all_passed = False

    def check_environment(self) -> None:
        """Verify .env file and Gemini API key."""
        env_path = PROJECT_ROOT / ".env"
        if not env_path.exists():
            self.log_result("Environment Config (.env)", "FAIL", "File .env not found on disk")
            return

        try:
            api_key = config.get_gemini_api_key()
            if len(api_key) < 10:
                self.log_result(
                    "Gemini API Key Format",
                    "FAIL",
                    f"API key seems suspiciously short ({len(api_key)} chars)",
                )
                return

            masked_key = f"{api_key[:6]}...{api_key[-4:]}"
            self.log_result(
                "Environment & Credentials",
                "PASS",
                f".env found, GEMINI_API_KEY={masked_key}, MODEL={config.MODEL_NAME}",
            )
        except Exception as exc:
            self.log_result("Environment & Credentials", "FAIL", str(exc))

    def check_database(self) -> None:
        """Verify SQLite initialization, schema, and write permissions."""
        try:
            init_db(DEFAULT_DB_PATH)
            if not DEFAULT_DB_PATH.exists():
                self.log_result("SQLite Persistence", "FAIL", "Database file was not created")
                return

            # Verify table and write transaction
            with get_db_connection(DEFAULT_DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='triage_history'"
                )
                table_exists = cursor.fetchone()[0] == 1
                if not table_exists:
                    self.log_result(
                        "SQLite Persistence", "FAIL", "Table 'triage_history' is missing"
                    )
                    return

                # Test insertion
                test_subj = f"__healthcheck_{int(time.time())}__"
                cursor.execute(
                    """
                    INSERT INTO triage_history (
                        subject, original_text, priority, priority_reason, summary,
                        actions_json, deadline, reply_required, reply_reason, category
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        test_subj,
                        "Health check ping body",
                        "LOW",
                        "Diagnostic automated ping",
                        "Diagnostic summary",
                        json.dumps(["Health task 1"]),
                        None,
                        0,
                        "No reply needed for diagnostics",
                        "WORK",
                    ),
                )
                row_id = cursor.lastrowid
                conn.commit()

                # Test read & cleanup
                cursor.execute("SELECT id, subject FROM triage_history WHERE id = ?", (row_id,))
                row = cursor.fetchone()
                if not row or row[1] != test_subj:
                    self.log_result(
                        "SQLite Persistence", "FAIL", "Failed to retrieve diagnostic test row"
                    )
                    return

                cursor.execute("DELETE FROM triage_history WHERE id = ?", (row_id,))
                conn.commit()

            self.log_result(
                "SQLite Persistence",
                "PASS",
                f"data/inbox_history.db writable (Schema: triage_history OK)",
            )
        except Exception as exc:
            self.log_result("SQLite Persistence", "FAIL", f"Database error: {exc}")

    def check_schemas(self) -> None:
        """Validate Pydantic v2 EmailTriageResult serialization and constraints."""
        try:
            sample_payload = {
                "priority": "HIGH",
                "priority_reason": "Executive board meeting schedule conflicts",
                "summary": "Urgent board meeting rescheduled to Friday morning.",
                "actions": ["Update calendar invitation", "Prepare Q3 slide deck"],
                "deadline": "2026-10-06T09:00:00Z",
                "reply_required": True,
                "reply_reason": "Confirmation of attendance required by end of day.",
                "category": "WORK",
            }
            model = EmailTriageResult.model_validate(sample_payload)
            serialized_json = model.model_dump_json()
            assert len(serialized_json) > 50

            # Test invalid priority constraint
            try:
                EmailTriageResult.model_validate({**sample_payload, "priority": "CRITICAL"})
                self.log_result(
                    "Schema Validation", "FAIL", "Failed to reject invalid priority literal"
                )
                return
            except Exception:
                pass  # Successfully caught invalid priority literal

            self.log_result(
                "Schema Validation",
                "PASS",
                "Pydantic v2 EmailTriageResult validated with strict typing and JSON serialization",
            )
        except Exception as exc:
            self.log_result("Schema Validation", "FAIL", f"Schema validation error: {exc}")

    def check_gemini_api(self) -> None:
        """Test live Gemini API network connectivity and latency."""
        try:
            from google import genai

            api_key = config.get_gemini_api_key()
            client = genai.Client(api_key=api_key)

            t0 = time.time()
            response = client.models.generate_content(
                model=config.MODEL_NAME,
                contents="Ping. Respond with exactly the word 'PONG'.",
            )
            latency_ms = int((time.time() - t0) * 1000)

            reply_text = response.text.strip() if response.text else ""
            if not reply_text:
                self.log_result("Gemini API Connectivity", "FAIL", "Received empty response text")
                return

            self.log_result(
                "Gemini API Connectivity",
                "PASS",
                f"Model={config.MODEL_NAME} responded in {latency_ms}ms ('{reply_text[:20]}')",
            )
        except Exception as exc:
            self.log_result("Gemini API Connectivity", "FAIL", f"API connection error: {exc}")

    def run_all(self) -> bool:
        """Execute all diagnostics and render the final report."""
        print("=" * 76)
        print("  AI INBOX ASSISTANT -- PRODUCTION DIAGNOSTIC SUITE")
        print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 76)

        print("\nRunning automated subsystem diagnostics...\n")
        self.check_environment()
        self.check_database()
        self.check_schemas()
        self.check_gemini_api()

        print("-" * 76)
        print(f"{'SUBSYSTEM':<28} | {'STATUS':<8} | {'DETAILS'}")
        print("-" * 76)
        for res in self.results:
            status_str = f"[{res['status']}]"
            print(f"{res['name']:<28} | {status_str:<8} | {res['details']}")
        print("-" * 76)

        if self.all_passed:
            print("\n" + "=" * 76)
            print("  ALL SUBSYSTEMS VERIFIED -- [READY FOR PRODUCTION]")
            print("=" * 76 + "\n")
            return True
        else:
            print("\n" + "!" * 76)
            print("  HEALTH CHECKS FAILED -- ATTENTION REQUIRED BEFORE RELEASE")
            print("!" * 76 + "\n")
            return False


if __name__ == "__main__":
    checker = HealthChecker()
    success = checker.run_all()
    sys.exit(0 if success else 1)
