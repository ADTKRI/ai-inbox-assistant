"""Top navigation bar component with integrated engine status pill and user profile."""

import streamlit as st


def render_navbar() -> None:
    """Render the clean Forest Green header bar with brand title, status pill, and user profile."""
    navbar_html = (
        '<div style="display: flex; justify-content: space-between; align-items: center; '
        'background-color: #154226; padding: 16px 28px; border-radius: 12px; color: #FFFFFF; '
        'margin-bottom: 24px; box-shadow: 0 4px 16px rgba(21, 66, 38, 0.18); '
        'font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif;">'
        '<div style="display: flex; align-items: center; gap: 12px;">'
        '<span style="font-size: 24px;">📥</span>'
        '<span style="font-size: 20px; font-weight: 800; letter-spacing: 0.5px; color: #FFFFFF;">INBOX ASSISTANT</span>'
        '</div>'
        '<div style="display: flex; align-items: center; gap: 8px; background: rgba(255, 255, 255, 0.15); '
        'padding: 6px 14px; border-radius: 20px; font-size: 13px; color: #FFFFFF;">'
        '<span style="font-size: 14px;">🏢</span>'
        '<span style="font-weight: 600; color: #FFFFFF;">Workspace</span>'
        '</div>'
        '</div>'
    )
    st.markdown(navbar_html, unsafe_allow_html=True)
