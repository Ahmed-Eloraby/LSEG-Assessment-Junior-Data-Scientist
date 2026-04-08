"""Page 2 — Asset Class Explorer (Q2)"""

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
from utils.ui import inject_css, page_title, section, metric_row, ACCENT, TEXT_MUTE

st.set_page_config(page_title="Asset Class · OpenPermID", page_icon="📊", layout="wide")
inject_css()
page_title(
    "📊",
    "Asset Class",
    "Asset class hierarchy, instrument counts, and edge structure",
)

df = load_triples("assetClass")
if df.empty:
    st.stop()

type_df = df[df["predicate"] == "type"]
asset_class_nodes = type_df[type_df["object"].str.contains("AssetClass", na=False)][
    "subject"
].unique()
asset_type_nodes = type_df[type_df["object"].str.contains("AssetType", na=False)][
    "subject"
].unique()

metric_row(
    [
        ("Asset Classes", str(len(asset_class_nodes))),
        ("Asset Sub-types", str(len(asset_type_nodes))),
        ("Edge Types", str(df["predicate"].nunique())),
        ("Total Triples", str(len(df))),
    ]
)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Analysis",
        "🗃️ Raw Data",
        "🔎 Predicate Explorer",
        "📋 Asset Table",
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
    section("Asset Classes & Sub-types")
    belongs = df[df["predicate"] == "belongsToAssetClass"][["subject", "object"]].copy()
    belongs["SubType_Label"] = (
        belongs["subject"].map(label_map).fillna(belongs["subject"])
    )
    belongs["AssetClass_Label"] = (
        belongs["object"].map(label_map).fillna(belongs["object"])
    )

    counts = (
        belongs.groupby("AssetClass_Label")["SubType_Label"]
        .count()
        .reset_index()
        .rename(columns={"SubType_Label": "Sub-type Count"})
        .sort_values("Sub-type Count", ascending=False)
    )

    col1, col2 = st.columns([2, 3])
    with col1:
        st.dataframe(counts, use_container_width=True, hide_index=True)
    with col2:
        if not belongs.empty:
            fig = px.sunburst(
                belongs,
                path=["AssetClass_Label", "SubType_Label"],
                template="plotly_dark",
                color="AssetClass_Label",
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
            fig.update_layout(
                paper_bgcolor="#ffffff", margin=dict(l=0, r=0, t=10, b=0), height=420
            )
            st.plotly_chart(fig, use_container_width=True)

    section("Instrument Count by Asset Class")
    cnt_df = df[df["predicate"] == "instrumentCount"].copy()
    if not cnt_df.empty:
        cnt_df["label"] = cnt_df["subject"].map(label_map).fillna(cnt_df["subject"])
        cnt_df["count_val"] = pd.to_numeric(cnt_df["object"], errors="coerce")
        cnt_df = cnt_df.dropna(subset=["count_val"]).sort_values(
            "count_val", ascending=False
        )
        fig2 = px.bar(
            cnt_df,
            x="label",
            y="count_val",
            template="plotly_dark",
            color="count_val",
            color_continuous_scale=[[0, "#1e3a5f"], [1, ACCENT]],
            labels={"label": "Asset Class", "count_val": "Instrument Count"},
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
    render_raw_tab(df, entity_key="assetClass")

# ── Tab 3: predicate explorer ─────────────────────────────────────────────────
with tab3:
    render_predicate_explorer_tab(df, entity_key="assetClass")

# ── Tab 4 ─────────────────────────────────────────────────────────────────────
with tab4:
    section("Asset Classes Details")
    pivoted = {}
    for _, row in df.iterrows():
        s, p, o = row["subject"], row["predicate"], row["object"]
        pivoted.setdefault(s, {"ID": s})[p] = o

    tbl = pd.DataFrame(pivoted.values())
    tbl.rename(
        columns={
            "label": "Name",
            "belongsToAssetClass": "Belong To",
            "instrumentCount": "Instrument Count",
        },
        inplace=True,
        errors="ignore",
    )
    tbl["Belong To"] = tbl["Belong To"].map(label_map).fillna(tbl["Belong To"])
    tbl["Belong To"] = tbl["Belong To"].map(label_map).fillna(tbl["Belong To"])
    st.dataframe(tbl, use_container_width=True, hide_index=True)
