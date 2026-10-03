"""AI Inbox Assistant - Streamlit Application Entrypoint."""

import streamlit as st

# Configure wide layout with custom page icon
st.set_page_config(
    page_title="AI Inbox Assistant",
    page_icon="📥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

import components.navbar as navbar
from components import render_input_panel, render_triage_cards
from schemas import EmailTriageResult
from services.analyzer import EmailAnalyzer
from services.storage import get_all_triages, init_db, save_triage

# Custom CSS for Design System: 14px rounded cards, 15-16px text, Forest Green accents
CUSTOM_CSS = """<style>
/* Canvas Background & Base Typography */
.stApp {
    background-color: #FAFBF9;
    color: #0F172A;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 15px;
}

/* Hide Default Streamlit Chrome */
#MainMenu, footer, header {
    visibility: hidden;
}

div[data-testid="stDecoration"],
div[data-testid="stStatusWidget"] {
    display: none;
}

/* Page Layout Spacing */
.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 2.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 1560px;
}

/* Elevated Card Container with Depth (16px radius, 28px padding, soft multi-layer shadow) */
div[data-testid="stVerticalBlock"] > div[style*="border"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 16px !important;
    padding: 28px !important;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.02) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 28px -4px rgba(0, 0, 0, 0.07), 0 10px 12px -5px rgba(0, 0, 0, 0.03) !important;
}

/* Structured Background Box for Action Checklist (Nested container inside active card) */
div[data-testid="stHorizontalBlock"] div[data-testid="column"]:first-child > div[data-testid="stVerticalBlock"] > div[style*="border"] {
    background-color: #F8FAFC !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    box-shadow: none !important;
    transform: none !important;
}
div[data-testid="stHorizontalBlock"] div[data-testid="column"]:first-child > div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
    box-shadow: none !important;
    transform: none !important;
}

/* Primary Action Button (Forest Green 48px, 16px Bold) */
button[kind="primary"] {
    background-color: #154226 !important;
    border-color: #154226 !important;
    color: #FFFFFF !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    height: 48px !important;
    border-radius: 10px !important;
    box-shadow: 0 2px 6px rgba(21, 66, 38, 0.2) !important;
    transition: all 0.2s ease !important;
}
button[kind="primary"]:hover {
    background-color: #0F331D !important;
    border-color: #0F331D !important;
    box-shadow: 0 4px 14px rgba(21, 66, 38, 0.3) !important;
}

/* Secondary Utility & Paginator Buttons with Smooth Hover */
button[kind="secondary"] {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    color: #334155 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    height: 38px !important;
    padding: 0 12px !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
button[kind="secondary"]:hover:not(:disabled) {
    background-color: #F8FAFC !important;
    border-color: #154226 !important;
    color: #154226 !important;
    transform: translateY(-1px);
}
button:disabled {
    opacity: 0.35 !important;
    cursor: not-allowed !important;
    background-color: #F8FAFC !important;
    border-color: #E2E8F0 !important;
    color: #94A3B8 !important;
    box-shadow: none !important;
    transform: none !important;
}

/* Inputs & Textareas (Crisp white background, dark charcoal text, clear border) */
div[data-baseweb="input"],
div[data-baseweb="textarea"] {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 10px !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}
div[data-baseweb="base-input"] {
    background-color: transparent !important;
    border: none !important;
}
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
.stTextInput input,
.stTextArea textarea {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    font-size: 15px !important;
    font-family: inherit !important;
    -webkit-text-fill-color: #0F172A !important;
    border: none !important;
}
div[data-baseweb="input"]:focus-within,
div[data-baseweb="textarea"]:focus-within {
    border-color: #154226 !important;
    box-shadow: 0 0 0 2px rgba(21, 66, 38, 0.18) !important;
}
div[data-baseweb="input"] input::placeholder,
div[data-baseweb="textarea"] textarea::placeholder,
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #94A3B8 !important;
    -webkit-text-fill-color: #94A3B8 !important;
}
div[data-testid="stTextInput"] label p,
div[data-testid="stTextArea"] label p {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #1E293B !important;
    margin-bottom: 2px !important;
}

/* Interactive Checkbox Typography & Strike-through */
div[data-testid="stCheckbox"] {
    margin-bottom: 6px !important;
}
div[data-testid="stCheckbox"]:last-child {
    margin-bottom: 0 !important;
}
div[data-testid="stCheckbox"] label span {
    font-size: 14.5px !important;
    color: #0F172A !important;
    line-height: 1.5 !important;
    font-weight: 500 !important;
}
div[data-testid="stCheckbox"] label del,
div[data-testid="stCheckbox"] label s {
    color: #94A3B8 !important;
    text-decoration: line-through !important;
}

/* Export Utility Buttons (Low-profile secondary style with smooth hover) */
div[data-testid="stDownloadButton"] button {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    color: #475569 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    height: 38px !important;
    padding: 0 10px !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
div[data-testid="stDownloadButton"] button:hover {
    background-color: #F8FAFC !important;
    border-color: #154226 !important;
    color: #154226 !important;
    transform: translateY(-1px);
}
</style>"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_resource
def get_email_analyzer() -> EmailAnalyzer:
    """Instantiate and cache the EmailAnalyzer engine."""
    return EmailAnalyzer()


def initialize_session_state() -> None:
    """Initialize SQLite database and load persistent records into session state."""
    init_db()

    if "current_card_index" not in st.session_state:
        st.session_state.current_card_index = 0

    if "triage_history" not in st.session_state:
        saved_records = get_all_triages()
        if saved_records:
            st.session_state.triage_history = saved_records
        else:
            # Seed initial benchmark record to SQLite so the board is immediately explore-ready
            benchmark_result = EmailTriageResult(
                priority="HIGH",
                priority_reason="Time-sensitive onboarding requirements with an explicit deadline of September 28.",
                summary="Requesting submission of updated resume and signed offer letter for internship onboarding, with reply confirmation required.",
                actions=[
                    "Upload updated resume",
                    "Upload offer letter",
                    "Reply to email to confirm document upload",
                ],
                deadline="September 28",
                reply_required=True,
                reply_reason="The sender explicitly requested confirmation once documents have been uploaded.",
                category="INTERNSHIP",
            )
            save_triage(
                subject="Internship Onboarding - Document Submission",
                raw_text="Please submit your updated resume and offer letter by September 28. Also confirm once the documents have been uploaded.",
                result=benchmark_result,
            )
            st.session_state.triage_history = get_all_triages()


# 1. Initialize State & Backend
initialize_session_state()
analyzer = get_email_analyzer()

# 2. Render Top Navigation Bar (Full Width across the top)
navbar.render_navbar()

# 3. Balanced 2-Column Layout: Left (38%) & Right (62%)
col_input, col_triage = st.columns([0.38, 0.62], gap="large")

# Left Column (38%): Email Input & Quick Presets
with col_input:
    with st.container(border=True):
        render_input_panel(analyze_callback=analyzer.analyze_email)

# Right Column (62%): Live Triage Board & Cards
with col_triage:
    render_triage_cards()
