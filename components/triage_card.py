"""Triage card component displaying analyzed emails with modern typography, interactive actions, and export tools."""

import streamlit as st
from schemas import EmailTriageResult
from services.exporter import export_to_csv, export_to_markdown
from services.storage import clear_all_triages, delete_triage

PRIORITY_CONFIG = {
    "HIGH": {
        "bg": "#FEF2F2",
        "color": "#B91C1C",
        "border": "#FCA5A5",
        "label": "HIGH PRIORITY",
    },
    "MEDIUM": {
        "bg": "#EFF6FF",
        "color": "#1D4ED8",
        "border": "#BFDBFE",
        "label": "MEDIUM PRIORITY",
    },
    "LOW": {
        "bg": "#F1F5F9",
        "color": "#475569",
        "border": "#CBD5E1",
        "label": "LOW PRIORITY",
    },
}


def render_triage_cards() -> None:
    """Render an interactive single-card slideshow/paginator for triaged emails."""
    history = st.session_state.get("triage_history", [])
    if "current_card_index" not in st.session_state:
        st.session_state.current_card_index = 0

    total_cards = len(history)

    # Safe index bounds checking
    if total_cards > 0:
        if st.session_state.current_card_index >= total_cards:
            st.session_state.current_card_index = total_cards - 1
        elif st.session_state.current_card_index < 0:
            st.session_state.current_card_index = 0

    # Top Header: Title & Clear All
    col_hdr, col_clear = st.columns([0.76, 0.24])
    with col_hdr:
        st.markdown(
            f'<h2 style="font-size: 24px; font-weight: 800; color: #0F172A; margin: 0; line-height: 1.3; '
            f'font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif;">'
            f'Triage Board <span style="font-size: 15px; font-weight: 600; color: #64748B;">({total_cards} saved)</span></h2>',
            unsafe_allow_html=True,
        )
    with col_clear:
        if history and st.button("Clear All", key="clear_all_cards", use_container_width=True):
            clear_all_triages()
            st.session_state.triage_history = []
            st.session_state.current_card_index = 0
            st.rerun()

    # Empty State
    if not history:
        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        empty_html = (
            '<div style="background-color: #FFFFFF; border: 2px dashed #CBD5E1; border-radius: 14px; '
            'padding: 64px 24px; text-align: center; color: #64748B; font-family: -apple-system, BlinkMacSystemFont, sans-serif;">'
            '<div style="font-size: 32px; margin-bottom: 12px;">📭</div>'
            '<div style="font-size: 18px; font-weight: 700; color: #0F172A; margin-bottom: 6px;">No emails triaged yet</div>'
            '<div style="font-size: 15px; color: #64748B; max-width: 400px; margin: 0 auto; line-height: 1.5;">'
            'Select a quick preset on the left or paste an incoming email to generate a structured executive triage card.'
            '</div>'
            '</div>'
        )
        st.markdown(empty_html, unsafe_allow_html=True)
        return

    # Interactive Navigation Bar: Previous, Counter Pill, Next, CSV, Markdown
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    col_prev, col_counter, col_next, col_csv, col_md = st.columns([0.20, 0.28, 0.20, 0.16, 0.16])

    curr_idx = st.session_state.current_card_index

    with col_prev:
        prev_disabled = (curr_idx <= 0)
        if st.button("◀ Previous", key="btn_prev_card", disabled=prev_disabled, use_container_width=True):
            st.session_state.current_card_index = max(0, curr_idx - 1)
            st.rerun()

    with col_counter:
        counter_html = (
            f'<div style="display: flex; justify-content: center; align-items: center; gap: 6px; height: 38px; '
            f'background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px; font-size: 13px; '
            f'font-weight: 700; color: #1E293B; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04); '
            f'font-family: -apple-system, BlinkMacSystemFont, sans-serif;">'
            f'<span style="color: #154226; font-size: 10px;">●</span>'
            f'<span>Email {curr_idx + 1} of {total_cards}</span>'
            f'</div>'
        )
        st.markdown(counter_html, unsafe_allow_html=True)

    with col_next:
        next_disabled = (curr_idx >= total_cards - 1)
        if st.button("Next ▶", key="btn_next_card", disabled=next_disabled, use_container_width=True):
            st.session_state.current_card_index = min(total_cards - 1, curr_idx + 1)
            st.rerun()

    with col_csv:
        csv_payload = export_to_csv(history)
        st.download_button(
            label="📄 CSV",
            data=csv_payload,
            file_name="inbox_triage_export.csv",
            mime="text/csv",
            use_container_width=True,
            help="Export all triaged emails to CSV",
        )

    with col_md:
        md_payload = export_to_markdown(history)
        st.download_button(
            label="📝 MD",
            data=md_payload,
            file_name="inbox_triage_briefing.md",
            mime="text/markdown",
            use_container_width=True,
            help="Export all triaged emails to Markdown briefing",
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Render ONLY the active card
    item = history[curr_idx]
    card_id = item["id"]
    result: EmailTriageResult = item["result"]
    subject = item["subject"]
    timestamp = item.get("timestamp", "")
    cfg = PRIORITY_CONFIG.get(result.priority, PRIORITY_CONFIG["LOW"])

    with st.container(border=True):
        time_html = (
            f'<span style="font-size: 12px; color: #64748B; font-weight: 500;">Triaged today at {timestamp}</span>'
            if timestamp
            else ""
        )

        # Card Top Row: Priority Badge + Reason + Labeled Timestamp
        header_html = (
            '<div style="display: flex; justify-content: space-between; align-items: center; '
            'flex-wrap: wrap; gap: 8px; margin-bottom: 12px; font-family: -apple-system, BlinkMacSystemFont, sans-serif;">'
            '<div style="display: flex; align-items: center; gap: 10px;">'
            f'<span style="background-color: {cfg["bg"]}; color: {cfg["color"]}; border: 1px solid {cfg["border"]}; '
            'font-size: 13px; font-weight: 700; padding: 4px 12px; border-radius: 9999px; letter-spacing: 0.05em; text-transform: uppercase;">'
            f'{cfg["label"]}'
            '</span>'
            f'<span style="font-size: 14px; color: #475569; font-weight: 500;">{result.priority_reason}</span>'
            '</div>'
            f'{time_html}'
            '</div>'
        )
        st.markdown(header_html, unsafe_allow_html=True)

        # Card Subject Line (20px Semibold #1E293B)
        st.markdown(
            f'<h3 style="font-size: 20px; font-weight: 700; color: #1E293B; margin: 4px 0 10px 0; '
            f'font-family: -apple-system, BlinkMacSystemFont, sans-serif;">{subject}</h3>',
            unsafe_allow_html=True,
        )

        # Executive Summary (Subtle soft green tint, deep forest green left border, #1E293B text)
        summary_html = (
            '<div style="background-color: #F0FDF4; border-left: 4px solid #154226; padding: 12px 16px; '
            'border-radius: 0 8px 8px 0; font-size: 15px; color: #1E293B; margin-bottom: 16px; line-height: 1.6; '
            'box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);">'
            f'<strong style="color: #154226;">Summary:</strong> {result.summary}'
            '</div>'
        )
        st.markdown(summary_html, unsafe_allow_html=True)

        # Actions & Details Grid
        col_actions, col_meta = st.columns([0.58, 0.42], gap="large")

        with col_actions:
            st.markdown(
                '<div style="font-size: 13px; font-weight: 700; color: #475569; text-transform: uppercase; '
                'letter-spacing: 0.05em; margin-bottom: 8px;">Actions Required</div>',
                unsafe_allow_html=True,
            )
            # Structured Background Box for Action Checklist
            with st.container(border=True):
                if not result.actions:
                    st.markdown(
                        '<div style="font-size: 14px; color: #94A3B8; font-style: italic;">No action items required.</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    if "actions_completed" not in item:
                        item["actions_completed"] = {i: False for i in range(len(result.actions))}

                    for act_idx, action_text in enumerate(result.actions):
                        chk_key = f"chk_{card_id}_{act_idx}"
                        was_checked = item["actions_completed"].get(act_idx, False)

                        # Visually format completed actions with strikethrough markdown
                        label_display = f"~~{action_text}~~" if was_checked else action_text

                        is_checked = st.checkbox(
                            label_display,
                            key=chk_key,
                            value=was_checked,
                        )

                        if is_checked != was_checked:
                            item["actions_completed"][act_idx] = is_checked
                            st.rerun()

        with col_meta:
            st.markdown(
                '<div style="font-size: 13px; font-weight: 700; color: #475569; text-transform: uppercase; '
                'letter-spacing: 0.05em; margin-bottom: 8px;">Details</div>',
                unsafe_allow_html=True,
            )
            deadline_val = result.deadline if result.deadline else "None specified"
            meta_html = (
                '<div style="display: flex; flex-direction: column; gap: 10px;">'
                '<div>'
                '<div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; '
                'letter-spacing: 0.05em; margin-bottom: 4px;">Category</div>'
                '<span style="display: inline-flex; align-items: center; background-color: #EEF2FF; '
                'border: 1px solid #C7D2FE; color: #4338CA; font-size: 12px; font-weight: 600; '
                'padding: 4px 10px; border-radius: 8px; letter-spacing: 0.03em; text-transform: uppercase;">'
                f'📁 {result.category}'
                '</span>'
                '</div>'
                '<div>'
                '<div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; '
                'letter-spacing: 0.05em; margin-bottom: 4px;">Deadline</div>'
                '<span style="display: inline-flex; align-items: center; gap: 6px; background-color: #FFFBEB; '
                'border: 1px solid #FDE68A; color: #B45309; font-size: 13px; font-weight: 600; '
                'padding: 6px 12px; border-radius: 8px;">'
                f'⏰ {deadline_val}'
                '</span>'
                '</div>'
                '</div>'
            )
            st.markdown(meta_html, unsafe_allow_html=True)

        # Reply Required Alert Banner (Soft rounded alert styling)
        if result.reply_required:
            reply_reason_text = result.reply_reason or "Response expected by sender."
            reply_html = (
                '<div style="background-color: #FEF3C7; border: 1px solid #FDE68A; color: #92400E; '
                'padding: 10px 16px; border-radius: 10px; font-size: 13.5px; line-height: 1.5; '
                'margin-top: 14px; margin-bottom: 12px; display: flex; align-items: flex-start; gap: 8px;">'
                '<span style="font-size: 15px; line-height: 1.2;">⚠️</span>'
                f'<div><strong style="color: #78350F;">Reply Required:</strong> {reply_reason_text}</div>'
                '</div>'
            )
        else:
            reply_reason_text = result.reply_reason or "Informational communication."
            reply_html = (
                '<div style="background-color: #ECFDF5; border: 1px solid #A7F3D0; color: #065F46; '
                'padding: 10px 16px; border-radius: 10px; font-size: 13.5px; line-height: 1.5; '
                'margin-top: 14px; margin-bottom: 12px; display: flex; align-items: flex-start; gap: 8px;">'
                '<span style="font-size: 15px; line-height: 1.2;">✅</span>'
                f'<div><strong style="color: #047857;">No Reply Needed:</strong> {reply_reason_text}</div>'
                '</div>'
            )
        st.markdown(reply_html, unsafe_allow_html=True)

        # Card Footer: Expander & Dismiss Button
        col_json, col_del = st.columns([0.84, 0.16])
        with col_json:
            with st.expander("Raw JSON Payload"):
                st.json(result.model_dump())
        with col_del:
            if st.button("Dismiss", key=f"del_{card_id}", help="Remove this card", use_container_width=True):
                if isinstance(card_id, int):
                    delete_triage(card_id)
                st.session_state.triage_history = [
                    h for h in st.session_state.triage_history if h["id"] != card_id
                ]
                if st.session_state.current_card_index >= len(st.session_state.triage_history):
                    st.session_state.current_card_index = max(0, len(st.session_state.triage_history) - 1)
                st.rerun()

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
