"""Page 3 — Industry Explorer (Q3) — includes PyVis network diagram"""

import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pandas as pd
import streamlit as st
import plotly.express as px
from utils.parser import (
    load_triples,
    predicate_counts,
    render_raw_tab,
    render_predicate_explorer_tab,
)
from utils.graph_viz import render_network
from utils.ui import inject_css, page_title, section, metric_row, ACCENT, TEXT_MUTE

st.set_page_config(page_title="Industry · OpenPermID", page_icon="🏭", layout="wide")
inject_css()
page_title(
    "🏭",
    "Industry",
    "Sectors, industries, and interactive network diagram",
)

df = load_triples("industry")
if df.empty:
    st.stop()

type_df = df[df["predicate"] == "type"]
n_sectors = type_df[type_df["object"].str.contains("BusinessSector", na=False)][
    "subject"
].nunique()
n_inds = type_df[type_df["object"].str.contains("Industry", na=False)][
    "subject"
].nunique()

metric_row(
    [
        ("Business Sectors", str(n_sectors)),
        ("Industries", str(n_inds)),
        ("Total Triples", str(len(df))),
    ]
)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📊 Analysis",
        "🕸️ Network Diagram",
        "🗃️ Raw Data",
        "🔎 Predicate Explorer",
        "📋 Industry Table",
    ]
)
label_map = dict(
    zip(
        df[df["predicate"] == "label"]["subject"],
        df[df["predicate"] == "label"]["object"],
    )
)

# ── Tab 1 ─────────────────────────────────────────────────────────────────────
with tab1:
    section("Industries per Business Sector")
    part_of_df = df[df["predicate"] == "isPartOf"][["subject", "object"]].copy()
    part_of_df["Industry"] = (
        part_of_df["subject"].map(label_map).fillna(part_of_df["subject"])
    )
    part_of_df["Sector"] = (
        part_of_df["object"].map(label_map).fillna(part_of_df["object"])
    )

    sector_counts = (
        part_of_df.groupby("Sector")["Industry"]
        .count()
        .reset_index()
        .rename(columns={"Industry": "Industry Count"})
        .sort_values("Industry Count", ascending=False)
    )
    col1, col2 = st.columns([3, 2])
    with col1:
        fig = px.bar(
            sector_counts,
            x="Industry Count",
            y="Sector",
            orientation="h",
            template="plotly_dark",
            color="Industry Count",
            color_continuous_scale=[[0, "#1e3a5f"], [1, ACCENT]],
        )
        fig.update_layout(
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            yaxis=dict(autorange="reversed"),
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=0),
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.dataframe(sector_counts, use_container_width=True, hide_index=True)

    section("All Industries by Sector (Sunburst)")
    if not part_of_df.empty:
        fig2 = px.sunburst(
            part_of_df,
            path=["Sector", "Industry"],
            template="plotly_dark",
            color="Sector",
            color_discrete_sequence=px.colors.qualitative.Vivid,
        )
        fig2.update_layout(
            paper_bgcolor="#ffffff", margin=dict(l=0, r=0, t=0, b=0), height=500
        )
        st.plotly_chart(fig2, use_container_width=True)

# ── Tab 2 ─────────────────────────────────────────────────────────────────────
with tab2:
    section("Interactive Network Diagram")
    st.markdown(
        f'<p style="color:{TEXT_MUTE};font-size:0.8rem;">'
        'Nodes: <span style="color:#f97316;">■</span> Sector &nbsp;'
        '<span style="color:#3b82f6;">■</span> Industry. '
        "Drag, scroll, and hover to explore.</p>",
        unsafe_allow_html=True,
    )
    max_n = st.slider("Max nodes to display", 20, 150, 80, step=10)
    physics_on = st.toggle("Enable physics simulation", value=True)
    edges = list(zip(df["subject"], df["predicate"], df["object"]))
    render_network(edges, max_nodes=max_n, height=540, physics=physics_on)

# ── Tab 3 ─────────────────────────────────────────────────────────────────────
with tab3:
    render_raw_tab(df, entity_key="industry")

# ── Tab 4: predicate explorer ─────────────────────────────────────────────────
with tab4:
    render_predicate_explorer_tab(df, entity_key="industry")

# ── Tab 5 ─────────────────────────────────────────────────────────────────────
with tab5:
    section("Industry Details")
    pivoted = {}
    for _, row in df.iterrows():
        s, p, o = row["subject"], row["predicate"], row["object"]
        pivoted.setdefault(s, {"ID": s})[p] = o

    tbl = pd.DataFrame(pivoted.values())
    tbl.rename(
        columns={
            "label": "Name",
            "isPartOf": "Part Of",
            "hasIndustry": "Industry",
        },
        inplace=True,
        errors="ignore",
    )
    tbl["Part Of"] = tbl["Part Of"].map(label_map).fillna(tbl["Part Of"])
    tbl["Industry"] = tbl["Industry"].map(label_map).fillna(tbl["Industry"])
    st.dataframe(tbl, use_container_width=True, hide_index=True)
