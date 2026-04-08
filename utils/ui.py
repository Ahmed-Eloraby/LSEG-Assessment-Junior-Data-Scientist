"""
Shared UI helpers: dark theme CSS injection and reusable metric row.
"""

import streamlit as st

# ── Dark theme palette ────────────────────────────────────────────────────────
ACCENT = "#f97316"  # orange
ACCENT2 = "#3b82f6"  # blue
BG_CARD = "#1e2130"
BG_PAGE = "#A8ADBB"
TEXT_MUTE = "#bac3cf"
FONT_COLOR_WHITE = "#FFFFFF"

GLOBAL_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background-color: {BG_PAGE};
    color: #e2e8f0;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: #161926 !important;
    border-right: 1px solid #2d3148;
}}
section[data-testid="stSidebar"] * {{
    color: {FONT_COLOR_WHITE} !important;
    font-size: 0.8rem;
}}
section[data-testid="stSidebar"] .stMarkdown p {{
    color: {FONT_COLOR_WHITE} !important;
    font-size: 0.8rem;
}}

/* Metric cards */
[data-testid="metric-container"] {{
    background: {BG_CARD};
    border: 1px solid #2d3148;
    border-radius: 12px;
    padding: 1rem 1.2rem;
}}
[data-testid="metric-container"] label {{
    color: {TEXT_MUTE} !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}
[data-testid="stMetricValue"] {{
    font-family: 'Space Mono', monospace !important;
    font-size: 2rem !important;
    color: {ACCENT} !important;
}}

/* Tabs */
[data-testid="stTabs"] button {{
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 0.05em;
}}
[data-testid="stTabs"] button[aria-selected="true"] {{
    border-bottom: 2px solid {ACCENT} !important;
    color: {ACCENT} !important;
}}

/* Dataframes */
[data-testid="stDataFrame"] {{
    border: 1px solid #2d3148;
    border-radius: 8px;
}}

/* Section headers */
.section-header {{
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: {TEXT_MUTE};
    border-bottom: 1px solid #2d3148;
    padding-bottom: 0.4rem;
    margin-bottom: 1rem;
    margin-top: 1.5rem;
}}

/* Page title band */
.page-title {{
    background: linear-gradient(90deg, #1e2130 0%, {BG_PAGE} 100%);
    border-left: 4px solid {ACCENT};
    padding: 0.8rem 1.2rem;
    border-radius: 0 8px 8px 0;
    margin-bottom: 1.5rem;
}}
.page-title h1 {{
    font-family: 'Space Mono', monospace;
    font-size: 1.4rem;
    margin: 0;
    color: #f1f5f9;
}}
.page-title p {{
    color: {TEXT_MUTE};
    font-size: 0.82rem;
    margin: 0.2rem 0 0 0;
}}

/* Info pill */
.pill {{
    display: inline-block;
    background: #2d3148;
    color: {ACCENT};
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    padding: 2px 10px;
    border-radius: 20px;
    margin: 2px;
}}
</style>
"""


def inject_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def page_title(icon: str, title: str, subtitle: str = ""):
    st.markdown(
        f"""<div class="page-title">
              <h1>{icon} {title}</h1>
              {"<p>" + subtitle + "</p>" if subtitle else ""}
            </div>""",
        unsafe_allow_html=True,
    )


def section(label: str):
    st.markdown(f'<div class="section-header">{label}</div>', unsafe_allow_html=True)


def metric_row(metrics: list[tuple[str, str]]):
    """Display a row of (label, value) metric cards."""
    cols = st.columns(len(metrics))
    for col, (label, value) in zip(cols, metrics):
        col.metric(label, value)
