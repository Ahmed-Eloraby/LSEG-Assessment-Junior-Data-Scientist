"""Page 7 — Instrument Explorer (Q7)"""

import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.express as px
from utils.parser import (
    load_triples,
    predicate_counts,
    render_raw_tab,
    render_predicate_explorer_tab,
)
from utils.ui import inject_css, page_title, section, metric_row, ACCENT

st.set_page_config(page_title="Instrument · OpenPermID", page_icon="🔧", layout="wide")
inject_css()
page_title(
    "🔧", "Instrument", "Q7 — Instrument types, asset class linkage, and issuers"
)

df = load_triples("instrument")
if df.empty:
    st.stop()

issuer_df = df[df["predicate"] == "isIssuedBy"]
ac_df = df[df["predicate"] == "hasAssetClass"]
status_df = df[df["predicate"] == "hasInstrumentStatus"]

metric_row(
    [
        ("Instruments", str(df["subject"].nunique())),
        ("Edges Count", str(df["predicate"].nunique())),
        ("Issuers", str(issuer_df["object"].nunique())),
    ]
)

tab1, tab2, tab3 = st.tabs(["📊 Analysis", "🗃️ Raw Data", "🔎 Predicate Explorer"])

# ── Tab 1 ─────────────────────────────────────────────────────────────────────
with tab1:
    section("Instrument Type Distribution")
    if not status_df.empty:
        rc = status_df["object"].value_counts().reset_index()
        rc.columns = ["Status", "Count"]
        col1, col2 = st.columns([2, 3])
        with col1:
            st.dataframe(rc, use_container_width=True, hide_index=True)
        with col2:
            fig = px.pie(
                rc,
                names="Status",
                values="Count",
                hole=0.5,
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Vivid,
            )
            fig.update_layout(
                paper_bgcolor="#ffffff", margin=dict(l=0, r=0, t=0, b=0), height=280
            )
            st.plotly_chart(fig, use_container_width=True)

    section("Asset Class Linkage")
    if not ac_df.empty:
        ac = ac_df["object"].value_counts().reset_index()
        ac.columns = ["Asset Class", "Count"]
        fig4 = px.treemap(
            ac,
            path=["Asset Class"],
            values="Count",
            template="plotly_dark",
            color="Count",
            color_continuous_scale=[[0, "#1e2130"], [1, ACCENT]],
        )
        fig4.update_layout(
            paper_bgcolor="#ffffff", margin=dict(l=0, r=0, t=0, b=0), height=280
        )
        st.plotly_chart(fig4, use_container_width=True)


# ── Tab 2 ─────────────────────────────────────────────────────────────────────
with tab2:
    render_raw_tab(df, entity_key="instrument")

# ── Tab 3: predicate explorer ─────────────────────────────────────────────────
with tab3:
    render_predicate_explorer_tab(df, entity_key="instrument")
