"""
Shared parsing utilities for OpenPermID .ntriples files.
Uses rdflib as the parser — it natively distinguishes URIRef from Literal,
so object-type classification is exact, not heuristic.
"""

import os
import pandas as pd
import streamlit as st
from rdflib import Graph, URIRef, Literal

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

FILE_MAP = {
    "currency": "OpenPermID-bulk-currency.ntriples",
    "assetClass": "OpenPermID-bulk-assetClass.ntriples",
    "industry": "OpenPermID-bulk-industry.ntriples",
    "organization": "OpenPermID-bulk-organization.ntriples",
    "person": "OpenPermID-bulk-person.ntriples",
    "quote": "OpenPermID-bulk-quote.ntriples",
    "instrument": "OpenPermID-bulk-instrument.ntriples",
}


# ── helpers ────────────────────────────────────────────────────────────────────
def parse_file_safe(graph, path):
    encodings = ["utf-8", "latin-1", "cp1252"]

    for enc in encodings:
        try:
            with open(path, "r", encoding=enc) as f:
                graph.parse(f, format="nt")
            print(f"Loaded {path} with {enc}")
            return
        except UnicodeDecodeError:
            continue

    print(f"Failed to parse {path}")


def _local_name(uri: str) -> str:
    """Return the local name portion of a URI (after last # or /)."""
    for sep in ("#", "/"):
        if sep in uri:
            return uri.rsplit(sep, 1)[-1]
    return uri


def _term_label(term) -> str:
    """Return a human-readable string for any rdflib term."""
    if isinstance(term, URIRef):
        return _local_name(str(term))
    if isinstance(term, Literal):
        return str(term)
    return str(term)


def _object_type(term) -> str:
    """Return the canonical object-type label for an rdflib term."""
    if isinstance(term, URIRef):
        return "URI"
    if isinstance(term, Literal):
        return "Literal"


# ── main loader ────────────────────────────────────────────────────────────────


@st.cache_data(show_spinner="Parsing graph data with rdflib…")
def load_triples(entity: str) -> pd.DataFrame:
    """
    Parse an .ntriples file with rdflib and return a
    DataFrame with columns:

        subject      – local name of the subject URI
        predicate    – local name of the predicate URI
        object       – human-readable value of the object
        object_type  – 'URI' | 'Literal'
        subject_uri  – full subject URI string (for graph building)
        object_uri   – full object URI string (for graph building; '' for literals)
    """
    filename = FILE_MAP.get(entity)
    if not filename:
        raise ValueError(f"Unknown entity: {entity}")

    plain_path = os.path.join(DATA_DIR, filename)

    g = Graph()

    if os.path.exists(plain_path):
        parse_file_safe(g, plain_path)

    else:
        st.warning(
            f"Data file not found for **{entity}**. "
            "Run `utils/generate_demo_data.py` to create demo data."
        )
        return pd.DataFrame(
            columns=[
                "subject",
                "predicate",
                "object",
                "object_type",
                "subject_uri",
                "object_uri",
            ]
        )

    rows = []
    for s, p, o in g:
        rows.append(
            {
                "subject": _term_label(s),
                "predicate": _term_label(p),
                "object": _term_label(o),
                "object_type": _object_type(o),
                "subject_uri": str(s),
                "object_uri": str(o) if isinstance(o, URIRef) else "",
            }
        )

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["subject", "predicate"]).reset_index(drop=True)

    return df


# ── analysis helpers ───────────────────────────────────────────────────────────


def predicate_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Sorted predicate frequency table (backward-compat helper)."""
    return (
        df["predicate"]
        .value_counts()
        .reset_index()
        .rename(columns={"predicate": "Predicate", "count": "Count"})
    )


@st.cache_data(show_spinner="Building predicate summary…")
def predicate_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Per-predicate summary table:
        Predicate | Count | % of Triples | Object Type | Example Values

    Object Type uses rdflib's exact classification stored in the
    'object_type' column — no heuristics needed.
        🔗 URI     — every object for this predicate is a URIRef
        📝 Literal — every object for this predicate is a Literal
    """
    total = len(df)
    rows = []

    for pred, grp in df.groupby("predicate"):
        count = len(grp)
        pct = round(count / total * 100, 1)
        types = grp["object_type"].value_counts()
        n_uri = types.get("URI", 0)
        n_lit = types.get("Literal", 0)

        if n_lit == 0:
            obj_type = "🔗 URI"
        elif n_uri == 0:
            obj_type = "📝 Literal"

        samples = grp["object"].dropna().unique()[:3]
        example = " · ".join(str(s)[:35] for s in samples)

        rows.append(
            {
                "Predicate": pred,
                "Count": count,
                "% of Triples": pct,
                "Object Type": obj_type,
                "Example Values": example,
            }
        )

    return (
        pd.DataFrame(rows).sort_values("Count", ascending=False).reset_index(drop=True)
    )


# ── shared raw-data tab renderer ──────────────────────────────────────────────


def render_raw_tab(df: pd.DataFrame, entity_key: str = "") -> None:
    """
    Render the standardised 'Raw Data' tab for any entity page.

    Section 1 — Predicate Summary
        Every predicate with: count, % of triples, object type
        (URI / Literal / Mixed — taken directly from rdflib, not guessed),
        and up to 3 example values.

    Section 2 — Full Triple Browser
        Fully searchable and filterable table of every triple.
        Filters: free-text search on subject/object, predicate selector,
        object-type selector.
    """
    from utils.ui import section, TEXT_MUTE

    # ── 1. Predicate Summary ──────────────────────────────────────────────────
    section("Predicate Summary")
    st.caption(
        "Every predicate in this entity's graph file. "
        "**Object Type** is determined precisely by rdflib — "
        "🔗 **URI** means the object is a link to another node in the graph; "
        "📝 **Literal** means it is a plain data value (string, number, boolean, date)."
    )

    summary = predicate_summary(df)

    def _type_style(val):
        colour = {"🔗": "#3b82f6", "📝": "#22c55e"}.get(str(val)[:2], "#94a3b8")
        return f"color:{colour}; font-weight:600"

    styled = (
        summary.style.map(_type_style, subset=["Object Type"])
        .bar(subset=["Count"], color="#f97316", vmin=0)
        .format({"% of Triples": "{:.1f}%"})
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown(
        f'<div style="font-size:0.74rem;color:{TEXT_MUTE};margin-top:4px 0 12px 0;">'
        '<span style="color:#3b82f6;">🔗 URI</span> — links to another graph node &nbsp;│&nbsp; '
        '<span style="color:#22c55e;">📝 Literal</span> — plain data value.'
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── 2. Full Triple Browser ────────────────────────────────────────────────
    section("Full Triple Browser")

    c1, c2, c3 = st.columns([3, 2, 1])
    with c1:
        search_text = st.text_input(
            "🔍 Search subjects or objects",
            placeholder="e.g. USD, Apple, sector-Technology …",
            key=f"raw_search_{entity_key}",
        )
    with c2:
        pred_options = ["— all predicates —"] + sorted(
            df["predicate"].unique().tolist()
        )
        pred_filter = st.selectbox(
            "Filter predicate",
            pred_options,
            key=f"raw_pred_{entity_key}",
        )
    with c3:
        obj_type_filter = st.selectbox(
            "Object type",
            ["— all —", "URI", "Literal"],
            key=f"raw_type_{entity_key}",
        )

    view = df.copy()
    if pred_filter != "— all predicates —":
        view = view[view["predicate"] == pred_filter]
    if obj_type_filter != "— all —":
        view = view[view["object_type"] == obj_type_filter]
    if search_text:
        mask = view["subject"].str.contains(search_text, case=False, na=False) | view[
            "object"
        ].str.contains(search_text, case=False, na=False)
        view = view[mask]

    parts = [f"**{len(view):,}** of **{len(df):,}** triples"]
    if pred_filter != "— all predicates —":
        parts.append(f"predicate = `{pred_filter}`")
    if obj_type_filter != "— all —":
        parts.append(f"type = `{obj_type_filter}`")
    if search_text:
        parts.append(f"search = `{search_text}`")
    st.caption(" · ".join(parts))

    display_cols = ["subject", "predicate", "object", "object_type"]
    st.dataframe(
        view[display_cols].reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
        height=460,
        column_config={
            "subject": st.column_config.TextColumn("Subject", width="medium"),
            "predicate": st.column_config.TextColumn("Predicate", width="medium"),
            "object": st.column_config.TextColumn("Object", width="large"),
            "object_type": st.column_config.TextColumn("Object Type", width="small"),
        },
    )


# ── predicate explorer tab renderer ──────────────────────────────────────────


def render_predicate_explorer_tab(df: pd.DataFrame, entity_key: str = "") -> None:
    """
    Render the '🔎 Predicate Explorer' tab.

    The user picks any predicate from a dropdown.  The tab then shows:
      • A summary info bar  (total triples, distinct values, object type)
      • A pie chart         (value distribution)
      • A bar chart         (value counts, sorted descending)
      • The raw value table (subject ↔ object for that predicate)

    Works for both URI-type and Literal-type predicates.
    For high-cardinality predicates (>50 distinct values) the charts show
    the top-N and group the remainder as "Other".
    """
    import plotly.express as px
    from utils.ui import section, TEXT_MUTE, ACCENT, BG_CARD

    TOP_N = 20  # max slices / bars before grouping into "Other"
    CHART_HEIGHT = 380

    # ── Predicate selector ────────────────────────────────────────────────────
    predicates_sorted = sorted(df["predicate"].unique().tolist())

    col_sel, col_info = st.columns([2, 3])
    with col_sel:
        chosen = st.selectbox(
            "Select a predicate to explore",
            predicates_sorted,
            key=f"pred_explorer_{entity_key}",
        )

    subset = df[df["predicate"] == chosen].copy()
    n_total = len(subset)
    obj_types = subset["object_type"].value_counts()
    n_uri = int(obj_types.get("URI", 0))
    n_lit = int(obj_types.get("Literal", 0))
    n_distinct = subset["object"].nunique()

    # Determine dominant type label + colour
    if n_lit == 0:
        type_label, type_colour = "🔗 URI", "#3b82f6"
    elif n_uri == 0:
        type_label, type_colour = "📝 Literal", "#22c55e"

    with col_info:
        st.markdown(
            f'<div style="background:{BG_CARD};border:1px solid #2d3148;'
            f"border-radius:10px;padding:0.8rem 1.2rem;margin-top:1.6rem;"
            f'display:flex;gap:2rem;align-items:center;">'
            f'<div><span style="color:{TEXT_MUTE};font-size:0.7rem;'
            f'text-transform:uppercase;letter-spacing:.08em;">Triples</span><br/>'
            f'<span style="font-family:Space Mono,monospace;font-size:1.3rem;'
            f'color:#f1f5f9;">{n_total:,}</span></div>'
            f'<div><span style="color:{TEXT_MUTE};font-size:0.7rem;'
            f'text-transform:uppercase;letter-spacing:.08em;">Distinct values</span><br/>'
            f'<span style="font-family:Space Mono,monospace;font-size:1.3rem;'
            f'color:#f1f5f9;">{n_distinct:,}</span></div>'
            f'<div><span style="color:{TEXT_MUTE};font-size:0.7rem;'
            f'text-transform:uppercase;letter-spacing:.08em;">Object type</span><br/>'
            f'<span style="font-family:Space Mono,monospace;font-size:1.1rem;'
            f'color:{type_colour};">{type_label}</span></div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── Value counts ──────────────────────────────────────────────────────────
    val_counts = (
        subset["object"]
        .value_counts()
        .reset_index()
        .rename(columns={"object": "Value", "count": "Count"})
    )

    # Group tail into "Other" when there are many distinct values
    if len(val_counts) > TOP_N:
        top = val_counts.head(TOP_N).copy()
        other_count = val_counts["Count"].iloc[TOP_N:].sum()
        other_row = pd.DataFrame(
            [
                {
                    "Value": f"Other ({len(val_counts) - TOP_N} values)",
                    "Count": other_count,
                }
            ]
        )
        val_counts_chart = pd.concat([top, other_row], ignore_index=True)
        st.caption(
            f"Showing top {TOP_N} of {n_distinct:,} distinct values — "
            f"remaining {n_distinct - TOP_N:,} grouped as 'Other' in the charts."
        )
    else:
        val_counts_chart = val_counts.copy()

    # ── Charts ────────────────────────────────────────────────────────────────
    section(f'Distribution of objects for  "{chosen}"')

    col_pie, col_bar = st.columns(2)

    # Pie chart
    with col_pie:
        fig_pie = px.pie(
            val_counts_chart,
            names="Value",
            values="Count",
            hole=0.45,
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig_pie.update_traces(
            textposition="inside",
            textinfo="percent+label",
            insidetextfont=dict(size=11),
        )
        fig_pie.update_layout(
            paper_bgcolor="#ffffff",
            margin=dict(l=0, r=0, t=30, b=0),
            height=CHART_HEIGHT,
            showlegend=(n_distinct <= 12),
            legend=dict(font=dict(size=10)),
            title=dict(
                text=f"<b>{chosen}</b> — pie",
                font=dict(size=13, color="#94a3b8"),
                x=0,
            ),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Bar chart
    with col_bar:
        fig_bar = px.bar(
            val_counts_chart,
            x="Count",
            y="Value",
            orientation="h",
            template="plotly_dark",
            color="Count",
            color_continuous_scale=[[0, "#1e3a5f"], [1, ACCENT]],
        )
        fig_bar.update_layout(
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
            xaxis=dict(title="Count"),
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=30, b=0),
            height=CHART_HEIGHT,
            title=dict(
                text=f"<b>{chosen}</b> — bar",
                font=dict(size=13, color="#94a3b8"),
                x=0,
            ),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Raw value table ───────────────────────────────────────────────────────
    section("Subjects & Objects for this Predicate")
    st.caption(f"{n_total:,} triples · {n_distinct:,} distinct object values")

    search_val = st.text_input(
        "🔍 Filter by subject or object value",
        placeholder="type to filter…",
        key=f"pred_exp_search_{entity_key}_{chosen}",
    )

    tbl = subset[["subject", "object", "object_type"]].copy()
    tbl.columns = ["Subject", "Object", "Object Type"]
    if search_val:
        mask = tbl["Subject"].str.contains(search_val, case=False, na=False) | tbl[
            "Object"
        ].str.contains(search_val, case=False, na=False)
        tbl = tbl[mask]

    st.dataframe(
        tbl.reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
        height=360,
        column_config={
            "Subject": st.column_config.TextColumn("Subject", width="medium"),
            "Object": st.column_config.TextColumn("Object", width="large"),
            "Object Type": st.column_config.TextColumn("Object Type", width="small"),
        },
    )
