"""Export utilities for email triage records (CSV and Markdown briefing)."""

import csv
import datetime
import io
from typing import Any


def export_to_csv(records: list[dict[str, Any]]) -> str:
    """Format triage records into CSV string for spreadsheets.

    Args:
        records: List of triage record dictionaries.

    Returns:
        str: Comma-separated values formatted string.
    """
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    # Header row
    writer.writerow([
        "ID",
        "Timestamp",
        "Subject",
        "Priority",
        "Category",
        "Deadline",
        "Reply Required",
        "Reply Reason",
        "Summary",
        "Actions",
        "Priority Reason",
    ])

    for item in records:
        res = item["result"]
        actions_str = " | ".join(res.actions) if res.actions else "None"
        writer.writerow([
            item["id"],
            item.get("timestamp", ""),
            item["subject"],
            res.priority,
            res.category,
            res.deadline or "None",
            "Yes" if res.reply_required else "No",
            res.reply_reason or "",
            res.summary,
            actions_str,
            res.priority_reason,
        ])

    return output.getvalue()


def export_to_markdown(records: list[dict[str, Any]]) -> str:
    """Format triage records into an executive markdown task briefing.

    Args:
        records: List of triage record dictionaries.

    Returns:
        str: Markdown formatted document.
    """
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    total_count = len(records)
    high_count = sum(1 for r in records if r["result"].priority == "HIGH")

    lines = [
        "# Executive Email Triage Briefing",
        f"**Generated:** {now_str} | **Total Triaged:** {total_count} | **High Urgency:** {high_count}",
        "",
        "---",
        "",
        "## Immediate Action Items",
    ]

    action_items_found = False
    for item in records:
        res = item["result"]
        if res.actions:
            for act in res.actions:
                action_items_found = True
                deadline_note = f" (Deadline: {res.deadline})" if res.deadline else ""
                lines.append(f"- [ ] **[{res.priority}]** {act} — *{item['subject']}*{deadline_note}")

    if not action_items_found:
        lines.append("- *No pending action items identified across current emails.*")

    lines.extend([
        "",
        "---",
        "",
        "## Detailed Triage Records",
        "",
    ])

    for idx, item in enumerate(records, 1):
        res = item["result"]
        deadline_text = res.deadline or "None specified"
        reply_text = f"Yes ({res.reply_reason})" if res.reply_required else "No"

        lines.extend([
            f"### {idx}. [{res.priority}] {item['subject']}",
            f"- **Category:** `{res.category}`",
            f"- **Deadline:** {deadline_text}",
            f"- **Reply Required:** {reply_text}",
            f"- **Priority Reason:** {res.priority_reason}",
            f"- **Summary:** {res.summary}",
        ])

        if res.actions:
            lines.append("- **Extracted Tasks:**")
            for act in res.actions:
                lines.append(f"  - [ ] {act}")

        lines.append("")

    return "\n".join(lines)
