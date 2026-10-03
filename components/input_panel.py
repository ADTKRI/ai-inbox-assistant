"""Input panel component for entering and analyzing emails with modern typography and chip presets."""

import datetime
from typing import Callable
import streamlit as st
from schemas import EmailTriageResult
from services.storage import save_triage

PRESET_EMAILS = [
    {
        "label": "Internship",
        "tooltip": "Preset 1: Sopra Steria benchmark onboarding email with document submission deadline",
        "subject": "Internship Onboarding - Document Submission",
        "body": "Please submit your updated resume and offer letter by September 28. Also confirm once the documents have been uploaded.",
    },
    {
        "label": "Standup Sync",
        "tooltip": "Preset 2: Team meeting follow-up and demo preparations",
        "subject": "Sprint 4 Standup & Demo Sync",
        "body": "Hi team, please prepare your 3-minute demo slides for the cross-functional sync tomorrow at 11 AM. Review the ticket backlog if you have pending PRs.",
    },
    {
        "label": "Newsletter",
        "tooltip": "Preset 3: Informational industry newsletter with no action required",
        "subject": "Tech Digest #142: Future of Generative Agents",
        "body": "Welcome to this week's issue covering new reasoning models, local LLM architectures, and our favorite open-source tools. No action needed, enjoy the weekend read!",
    },
]


def render_input_panel(analyze_callback: Callable[[str, str], EmailTriageResult]) -> None:
    """Render the Email Analysis Panel container with presets, inputs, and flow breadcrumbs.

    Args:
        analyze_callback: Function accepting (raw_text, subject) that returns an EmailTriageResult.
    """
    st.markdown(
        '<h2 style="font-size: 24px; font-weight: 800; color: #0F172A; margin: 0 0 16px 0; '
        'font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif;">'
        'Email Analysis</h2>',
        unsafe_allow_html=True,
    )

    # Initialize session state for input fields if not present
    if "subject_field" not in st.session_state:
        st.session_state.subject_field = ""
    if "body_field" not in st.session_state:
        st.session_state.body_field = ""

    # Quick Presets Section (Chip style buttons)
    st.markdown(
        '<div style="font-size: 13px; font-weight: 700; color: #475569; letter-spacing: 0.05em; '
        'text-transform: uppercase; margin-bottom: 8px;">Quick Presets</div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(len(PRESET_EMAILS))
    for i, preset in enumerate(PRESET_EMAILS):
        with cols[i]:
            if st.button(
                preset["label"],
                key=f"preset_btn_{i}",
                help=preset["tooltip"],
                use_container_width=True,
            ):
                st.session_state.subject_field = preset["subject"]
                st.session_state.body_field = preset["body"]
                st.rerun()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Form Inputs bound to key-backed state
    subject = st.text_input(
        "Subject",
        placeholder="e.g. Internship Onboarding - Document Submission",
        key="subject_field",
    )

    body = st.text_area(
        "Email Body",
        placeholder="Paste full email text here...",
        height=220,
        key="body_field",
    )

    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

    # Analyze Button (48px prominent action)
    if st.button("Analyze Email", type="primary", use_container_width=True):
        if not body or not body.strip():
            st.error("Email body text cannot be empty.")
        else:
            with st.spinner("Extracting operational metadata with Gemini..."):
                try:
                    result = analyze_callback(body.strip(), subject.strip())
                    clean_subject = subject.strip() or "Untitled Email"
                    row_id = save_triage(
                        subject=clean_subject,
                        raw_text=body.strip(),
                        result=result,
                    )
                    new_record = {
                        "id": row_id,
                        "subject": clean_subject,
                        "body": body.strip(),
                        "result": result,
                        "timestamp": datetime.datetime.now().strftime("%I:%M %p"),
                        "actions_completed": {i: False for i in range(len(result.actions))},
                    }
                    if "triage_history" not in st.session_state:
                        st.session_state.triage_history = []
                    st.session_state.triage_history.insert(0, new_record)
                    st.session_state.current_card_index = 0
                    st.toast("Email analyzed and saved to database!", icon="✅")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Analysis Error: {exc}")

    # Analysis Flow Breadcrumbs
    st.markdown(
        '<div style="margin-top: 20px; padding-top: 14px; border-top: 1px solid #E2E8F0;">'
        '<div style="font-size: 12px; font-weight: 700; color: #64748B; letter-spacing: 0.05em; '
        'text-transform: uppercase; margin-bottom: 8px;">Pipeline Flow</div>'
        '<div style="display: flex; align-items: center; justify-content: space-between; '
        'font-size: 12px; font-weight: 600; font-family: -apple-system, BlinkMacSystemFont, sans-serif;">'
        '<span style="background: #EBF5EF; color: #154226; padding: 5px 10px; border-radius: 6px; border: 1px solid #C4E3D0;">1. Input</span>'
        '<span style="color: #94A3B8;">➔</span>'
        '<span style="background: #EBF5EF; color: #154226; padding: 5px 10px; border-radius: 6px; border: 1px solid #C4E3D0;">2. Gemini</span>'
        '<span style="color: #94A3B8;">➔</span>'
        '<span style="background: #EBF5EF; color: #154226; padding: 5px 10px; border-radius: 6px; border: 1px solid #C4E3D0;">3. JSON</span>'
        '<span style="color: #94A3B8;">➔</span>'
        '<span style="background: #EBF5EF; color: #154226; padding: 5px 10px; border-radius: 6px; border: 1px solid #C4E3D0;">4. SQLite</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )
