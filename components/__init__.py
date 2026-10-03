"""Modular UI components for the AI Inbox Assistant Streamlit application."""

from .navbar import render_navbar
from .input_panel import render_input_panel
from .triage_card import render_triage_cards

__all__ = [
    "render_navbar",
    "render_input_panel",
    "render_triage_cards",
]
