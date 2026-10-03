"""Data schemas for email triage and analysis using Pydantic v2."""

from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


PriorityLevel = Literal["HIGH", "MEDIUM", "LOW"]

CategoryType = Literal[
    "INTERNSHIP",
    "COLLEGE",
    "WORK",
    "FINANCE",
    "SHOPPING",
    "NEWSLETTER",
    "PERSONAL",
]


class EmailTriageResult(BaseModel):
    """Structured triage and categorization output for an incoming email.

    Attributes:
        priority: Urgency assessment of the email ('HIGH', 'MEDIUM', or 'LOW').
        priority_reason: Reasoning behind the assigned priority level.
        summary: Concise summary of the email content.
        actions: List of concrete action items or follow-ups extracted.
        deadline: ISO date string or textual deadline, or None if no deadline exists.
        reply_required: Boolean flag indicating whether the recipient needs to reply.
        reply_reason: Explanation of why a reply is or is not needed.
        category: Primary categorization bucket for the email.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    priority: PriorityLevel = Field(
        ...,
        description="Assigned urgency level: HIGH, MEDIUM, or LOW.",
    )
    priority_reason: str = Field(
        ...,
        description="Justification for the assigned priority level.",
    )
    summary: str = Field(
        ...,
        description="Concise summary of the email content and core message.",
    )
    actions: list[str] = Field(
        default_factory=list,
        description="List of action items, tasks, or follow-ups extracted from the email.",
    )
    deadline: Optional[str] = Field(
        default=None,
        description="ISO date string or explicit deadline text if present; None otherwise.",
    )
    reply_required: bool = Field(
        ...,
        description="Whether an explicit response or reply is required.",
    )
    reply_reason: Optional[str] = Field(
        default=None,
        description="Rationale for why a reply is required or not.",
    )
    category: CategoryType = Field(
        ...,
        description="Classification category: INTERNSHIP, COLLEGE, WORK, FINANCE, SHOPPING, NEWSLETTER, or PERSONAL.",
    )
