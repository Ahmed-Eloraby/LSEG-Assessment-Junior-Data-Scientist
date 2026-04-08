"""Page 1 — Currency Explorer (Q1)"""

import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.parser import (
    load_triples,
    predicate_counts,
    render_raw_tab,
    render_predicate_explorer_tab,
)
from utils.ui import (
    inject_css,
    page_title,
    section,
    metric_row,
    ACCENT,
    BG_CARD,
    TEXT_MUTE,
)

st.set_page_config(page_title="Currency · OpenPermID", page_icon="💱", layout="wide")
inject_css()
page_title(
    "💱",
    "Currency",
    "Currency nodes, ISO codes, issuing countries, and graph edges",
)

df = load_triples("currency")
if df.empty:
    st.stop()

n_nodes = df["subject"].nunique()
n_predicates = df["predicate"].nunique()
n_triples = len(df)

metric_row(
    [
        ("Currency Nodes", str(n_nodes)),
        ("Edges Count", str(n_predicates)),
        ("Total Triples", str(n_triples)),
    ]
)

tab1, tab2, tab3 = st.tabs(
    [
        "📋 Currency Table",
        "🗃️ Raw Data",
        "🔎 Predicate Explorer",
    ]
)

# ── Tab 1: pivoted currency details ──────────────────────────────────────────
with tab1:
    section("Currency Details")
    pivoted = {}
    for _, row in df.iterrows():
        s, p, o = row["subject"], row["predicate"], row["object"]
        pivoted.setdefault(s, {"ID": s})[p] = o

    tbl = pd.DataFrame(pivoted.values())
    tbl.rename(
        columns={
            "label": "Name",
            "isoCode": "ISO Code",
            "issuingCountry": "Country",
            "currencySymbol": "Symbol",
            "isActive": "Active",
        },
        inplace=True,
        errors="ignore",
    )
    st.dataframe(tbl, use_container_width=True, hide_index=True)

# ── Tab 2: raw data ───────────────────────────────────────────────────────────
with tab2:
    render_raw_tab(df, entity_key="currency")

# ── Tab 3: predicate explorer ─────────────────────────────────────────────────
with tab3:
    render_predicate_explorer_tab(df, entity_key="currency")
