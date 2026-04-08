"""Page 4 — Organization Explorer (Q4)"""

import os, sys
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.express as px
from utils.parser import (
    load_triples,
    render_raw_tab,
    render_predicate_explorer_tab,
)
from utils.ui import inject_css, page_title, section, metric_row, ACCENT

st.set_page_config(
    page_title="Organization · OpenPermID", page_icon="🏢", layout="wide"
)
inject_css()
page_title(
    "🏢", "Organization", "Q4 — Companies, countries, sectors, and organisation types"
)

df = load_triples("organization")
if df.empty:
    st.stop()

country_df = df[df["predicate"] == "domicileCountry"]

metric_row(
    [
        ("Organizations", str(df["subject"].nunique())),
        ("Predicate Types", str(df["predicate"].nunique())),
        ("Total Triples", str(len(df))),
    ]
)
df_industry = load_triples("industry")
label_map_industry = dict(
    zip(
        df_industry[df_industry["predicate"] == "label"]["subject"],
        df_industry[df_industry["predicate"] == "label"]["object"],
    )
)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Analysis",
        "🗃️ Raw Data",
        "🔎 Predicate Explorer",
        "📋 Organizations Table",
    ]
)

# ── Tab 1 ─────────────────────────────────────────────────────────────────────
with tab1:
    section("Organizations by Domicile Country")
    label_map = dict(
        zip(
            df[df["predicate"] == "label"]["subject"],
            df[df["predicate"] == "label"]["object"],
        )
    )
    print(label_map)
    print("Balabizo")
    if not country_df.empty:

        cc = country_df["object"].value_counts().reset_index()
        cc.columns = ["Country", "Count"]
        fig = px.bar(
            cc.head(20),
            x="Country",
            y="Count",
            template="plotly_dark",
            color="Count",
            color_continuous_scale=[[0, "#1e3a5f"], [1, ACCENT]],
        )
        fig.update_layout(
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=0),
            height=320,
        )
        st.plotly_chart(fig, use_container_width=True)

    section("Organisation Type Breakdown")
    type_df = df[df["predicate"] == "organizationType"]
    if not type_df.empty:
        tc = type_df["object"].value_counts().reset_index()
        tc.columns = ["Type", "Count"]
        col1, col2 = st.columns([1, 2])
        with col1:
            st.dataframe(tc, use_container_width=True, hide_index=True)
        with col2:
            fig2 = px.pie(
                tc,
                names="Type",
                values="Count",
                hole=0.5,
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
            fig2.update_layout(
                paper_bgcolor="#ffffff", margin=dict(l=0, r=0, t=0, b=0), height=280
            )
            st.plotly_chart(fig2, use_container_width=True)

    section("Sector Distribution")
    sec_df = df[df["predicate"] == "hasIndustrySector"]
    if not sec_df.empty:
        sc = sec_df["object"].value_counts().reset_index()
        sc.columns = ["Sector", "Count"]
        st.dataframe(sc, use_container_width=True, hide_index=True)

    section("All Organizations by domicileCountry (Sunburst)")
    domicileCountry_df = df[df["predicate"] == "domicileCountry"].copy()
    domicileCountry_df["subject"] = (
        domicileCountry_df["subject"]
        .map(label_map)
        .fillna(domicileCountry_df["subject"])
    )

    if not domicileCountry_df.empty:
        fig2 = px.sunburst(
            domicileCountry_df,
            path=["object", "subject"],
            template="plotly_dark",
            color="object",
            color_discrete_sequence=px.colors.qualitative.Vivid,
        )
        fig2.update_layout(
            paper_bgcolor="#ffffff", margin=dict(l=0, r=0, t=0, b=0), height=500
        )
        st.plotly_chart(fig2, use_container_width=True)

    section("All Organizations by sector (Sunburst)")
    sector_df = df[df["predicate"] == "hasIndustrySector"].copy()
    sector_df["subject"] = (
        sector_df["subject"].map(label_map).fillna(sector_df["subject"])
    )
    sector_df["object"] = (
        sector_df["object"].map(label_map_industry).fillna(sector_df["object"])
    )
    if not sector_df.empty:
        fig2 = px.sunburst(
            sector_df,
            path=["object", "subject"],
            template="plotly_dark",
            color="object",
            color_discrete_sequence=px.colors.qualitative.Vivid,
        )
        fig2.update_layout(
            paper_bgcolor="#ffffff", margin=dict(l=0, r=0, t=0, b=0), height=500
        )
        st.plotly_chart(fig2, use_container_width=True)
# ── Tab 2 ─────────────────────────────────────────────────────────────────────
with tab2:
    render_raw_tab(df, entity_key="organization")

# ── Tab 3: predicate explorer ─────────────────────────────────────────────────
with tab3:
    render_predicate_explorer_tab(df, entity_key="organization")

# ── Tab 4 ─────────────────────────────────────────────────────────────────────
with tab4:
    section("Industry Details")
    pivoted = {}
    for _, row in df.iterrows():
        s, p, o = row["subject"], row["predicate"], row["object"]
        pivoted.setdefault(s, {"ID": s})[p] = o

    tbl = pd.DataFrame(pivoted.values())

    tbl["hasIndustrySector"] = (
        tbl["hasIndustrySector"]
        .map(label_map_industry)
        .fillna(tbl["hasIndustrySector"])
    )
    st.dataframe(tbl, use_container_width=True, hide_index=True)
