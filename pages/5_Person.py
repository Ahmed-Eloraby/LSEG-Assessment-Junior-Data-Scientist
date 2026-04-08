"""Page 5 — Person Explorer (Q5)"""

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
from utils.ui import inject_css, page_title, section, metric_row, ACCENT

st.set_page_config(page_title="Person · OpenPermID", page_icon="👤", layout="wide")
inject_css()
page_title("👤", "Person", "Q5 — Executives, roles, and employer relationships")

df = load_triples("person")

df_org = load_triples("organization")

label_map_org = dict(
    zip(
        df_org[df_org["predicate"] == "label"]["subject"],
        df_org[df_org["predicate"] == "label"]["object"],
    )
)
if df.empty:
    st.stop()
# print("Balabizo")
# print(df["predicate"].unique())

role_df = df[df["predicate"] == "hasRole"]
gender_df = df[df["predicate"] == "gender"]
employer_df = df[df["predicate"] == "employedBy"].copy()
employer_df["object"] = (
    employer_df["object"].map(label_map_org).fillna(employer_df["object"])
)

metric_row(
    [
        ("People", str(df["subject"].nunique())),
        ("Distinct Roles", str(role_df["object"].nunique())),
        ("Gender Count", str(gender_df["object"].nunique())),
        ("Total Triples", str(len(df))),
    ]
)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Analysis",
        "🗃️ Raw Data",
        "🔎 Predicate Explorer",
        "📋 Person Table",
    ]
)

# ── Tab 1 ─────────────────────────────────────────────────────────────────────
with tab1:
    section("Role Distribution")
    if not role_df.empty:
        rc = role_df["object"].value_counts().reset_index()
        rc.columns = ["Role", "Count"]
        col1, col2 = st.columns([2, 3])
        with col1:
            st.dataframe(rc, use_container_width=True, hide_index=True)
        with col2:
            fig = px.pie(
                rc,
                names="Role",
                values="Count",
                hole=0.5,
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Vivid,
            )
            fig.update_layout(
                paper_bgcolor="#ffffff", margin=dict(l=0, r=0, t=0, b=0), height=280
            )
            st.plotly_chart(fig, use_container_width=True)

    section("gender Distribution")
    if not gender_df.empty:
        gc = gender_df["object"].value_counts().reset_index()
        gc.columns = ["gender", "Count"]
        col1, col2 = st.columns([2, 3])
        with col1:
            st.dataframe(gc, use_container_width=True, hide_index=True)
        with col2:
            fig = px.pie(
                gc,
                names="gender",
                values="Count",
                hole=0.5,
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Vivid,
            )
            fig.update_layout(
                paper_bgcolor="#ffffff", margin=dict(l=0, r=0, t=0, b=0), height=280
            )
            st.plotly_chart(fig, use_container_width=True)

    section("People Directory")
    label_map = dict(
        zip(
            df[df["predicate"] == "label"]["subject"],
            df[df["predicate"] == "label"]["object"],
        )
    )
    role_map = dict(zip(role_df["subject"], role_df["object"]))
    employer_map = dict(zip(employer_df["subject"], employer_df["object"]))

    people_tbl = pd.DataFrame(
        [
            {
                "Name": label_map.get(pid, pid),
                "Role": role_map.get(pid, "—"),
                "Employer": employer_map.get(pid, "—"),
            }
            for pid in df["subject"].unique()
        ]
    ).drop_duplicates()

    search = st.text_input("Search by name", placeholder="e.g. Cook, Buffett…")
    if search:
        people_tbl = people_tbl[
            people_tbl["Name"].str.contains(search, case=False, na=False)
        ]
    st.dataframe(people_tbl, use_container_width=True, hide_index=True)

# ── Tab 2 ─────────────────────────────────────────────────────────────────────
with tab2:
    render_raw_tab(df, entity_key="person")

# ── Tab 3: predicate explorer ─────────────────────────────────────────────────
with tab3:
    render_predicate_explorer_tab(df, entity_key="person")


# ── Tab 4 ─────────────────────────────────────────────────────────────────────
with tab4:
    section("Industry Details")
    pivoted = {}
    for _, row in df.iterrows():
        s, p, o = row["subject"], row["predicate"], row["object"]
        pivoted.setdefault(s, {"ID": s})[p] = o

    tbl = pd.DataFrame(pivoted.values())

    tbl["employedBy"] = tbl["employedBy"].map(label_map_org).fillna(tbl["employedBy"])
    st.dataframe(tbl, use_container_width=True, hide_index=True)
