"""Page 6 — Quote Explorer (Q6)"""

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

st.set_page_config(page_title="Quote · OpenPermID", page_icon="📈", layout="wide")
inject_css()
page_title("📈", "Quote", "Q6 — Exchange listings, quote types, and currency linkage")

df = load_triples("quote")
if df.empty:
    st.stop()

exch_df = df[df["predicate"] == "listedOn"]
ccy_df = df[df["predicate"] == "quoteCurrency"]
type_df = df[df["predicate"] == "type"]

metric_row(
    [
        ("Quote Nodes", str(df["subject"].nunique())),
        ("Exchanges", str(exch_df["object"].nunique())),
        ("Edges Count", str(df["predicate"].nunique())),
        ("Quotes Types", str(type_df["object"].nunique())),
        ("Total Triples", str(len(df))),
    ]
)

tab1, tab2, tab3 = st.tabs(["📊 Analysis", "🗃️ Raw Data", "🔎 Predicate Explorer"])

# ── Tab 1 ─────────────────────────────────────────────────────────────────────
with tab1:
    section("Quote Type Distribution")
    if not type_df.empty:
        tc = type_df["object"].value_counts().reset_index()
        tc.columns = ["Quote Type", "Count"]
        col1, col2 = st.columns([2, 3])
        with col1:
            st.dataframe(tc, use_container_width=True, hide_index=True)
        with col2:
            fig = px.pie(
                tc,
                names="Quote Type",
                values="Count",
                hole=0.5,
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
            fig.update_layout(
                paper_bgcolor="#ffffff", margin=dict(l=0, r=0, t=0, b=0), height=280
            )
            st.plotly_chart(fig, use_container_width=True)

    section("Quotes by Exchange")
    if not exch_df.empty:
        ec = exch_df["object"].value_counts().reset_index()
        ec.columns = ["Exchange", "Quote Count"]
        fig2 = px.bar(
            ec,
            x="Exchange",
            y="Quote Count",
            template="plotly_dark",
            color="Quote Count",
            color_continuous_scale=[[0, "#1e3a5f"], [1, ACCENT]],
        )
        fig2.update_layout(
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=0),
            height=300,
        )
        st.plotly_chart(fig2, use_container_width=True)


# ── Tab 2 ─────────────────────────────────────────────────────────────────────
with tab2:
    render_raw_tab(df, entity_key="quote")

# ── Tab 3: predicate explorer ─────────────────────────────────────────────────
with tab3:
    render_predicate_explorer_tab(df, entity_key="quote")
