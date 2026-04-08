"""
Home.py — OpenPermID Graph Explorer
Entry point for the Streamlit multi-page app.
"""

import os, sys

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from utils.ui import inject_css, ACCENT, ACCENT2, BG_CARD, TEXT_MUTE

st.set_page_config(
    page_title="OpenPermID Explorer",
    page_icon="🏚️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ── Sidebar ───────────────────────────────────────────────────────────────────
# import streamlit as st

import streamlit as st

# CSS to make sidebar flex
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] > div {
            display: flex;
            flex-direction: column;
            height: 100%;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# Push content down + signature
st.sidebar.markdown(
    """
    <div style="flex:1;"></div>
    <hr>
    <div style="text-align:center; font-size:12px; color:gray;">
        Made by Ahmed Eloraby
    </div>
    <div style="text-align:center; font-size:12px; color:gray;">
        ahmed.a.eloraby@gmail.com
    </div>
    """,
    unsafe_allow_html=True,
)
# def apply_sidebar_style():
#     st.markdown(
#         """
#         <style>
#         section[data-testid="stSidebar"] * {
#             color: white !important;
#         }
#         </style>
#         """,
#         unsafe_allow_html=True,
#     )


# with st.sidebar:
#     st.markdown(
#         f"""<div style="padding:1rem 0 0.5rem 0;">
#               <span style="font-family:'Space Mono',monospace;font-size:1rem;
#                            color:{ACCENT};font-weight:700;">◆ OpenPermID</span><br/>
#               <span style="color:{TEXT_MUTE};font-size:0.75rem;">Graph Data Explorer</span>
#             </div>""",
#         unsafe_allow_html=True,
#     )
#     st.markdown("---")
#     st.markdown(
#         f"""<p>Navigate using the <strong>pages</strong> below.<br/>
#         Each page corresponds to one entity in the assessment.</p>""",
#         unsafe_allow_html=True,
#     )
#     st.markdown("---")
#     st.caption("Built with Python · RDFLib · Plotly · Streamlit")

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="text-align:center;padding:3rem 1rem 2rem;">
      <div style="font-family:'Space Mono',monospace;font-size:2.8rem;
                  color:{ACCENT2};line-height:1.1;">
        OpenPermID<br/>
        <span style="color:{ACCENT};">Graph Explorer</span>
      </div>
      <p style="color:{TEXT_MUTE};font-size:1rem;margin-top:1rem;max-width:560px;
                margin-left:auto;margin-right:auto;">
        Interactive exploration of financial knowledge graph data —
        currencies, asset classes, industries, organizations, people,
        quotes, and instruments.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Entity cards grid ─────────────────────────────────────────────────────────
ENTITIES = [
    ("💱", "Currency", "Currency nodes, ISO codes, issuing countries"),
    ("📊", "Asset_Class", "Asset class hierarchy and instrument counts"),
    ("🏭", "Industry", "Sectors, industries, and network diagram"),
    ("🏢", "Organization", "Public companies, countries, sectors"),
    ("👤", "Person", "Executives, roles, employer links"),
    ("📈", "Quote", "Exchange listings, quote types, currencies"),
    ("🔧", "Instrument", "Instrument types, asset class, issuers"),
]

cols = st.columns(4)
for i, (icon, name, desc) in enumerate(ENTITIES):
    with cols[i % 4]:
        # Notice the <a> tag wrapping the <div> and pointing to /?page={i}
        st.markdown(
            f"""
            <a href="/{name}" target="_self" style="text-decoration:none; color:inherit;">
                <div style="background:{BG_CARD};border:1px solid #2d3148;border-radius:12px;
                            padding:1.2rem;margin-bottom:1rem;cursor:pointer;
                            transition:border-color 0.2s; height:200px" 
                     onmouseover="this.style.borderColor='{ACCENT}'"
                     onmouseout="this.style.borderColor='#2d3148'">
                  <div style="font-size:1.8rem;margin-bottom:0.4rem;">{icon}</div>
                  <div style="font-family:'Space Mono',monospace;font-size:0.9rem;
                              color:#f1f5f9;font-weight:700;">{name}</div>
                  <div style="font-size:0.78rem;color:{TEXT_MUTE};line-height:1.5;">{desc}</div>
                </div>
            </a>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")

# ── Setup instructions ────────────────────────────────────────────────────────
with st.expander("⚙️ Setup Instructions", expanded=False):
    st.markdown(
        """
    **1. Install dependencies**
    ```bash
    pip install streamlit rdflib pandas plotly pyvis networkx
    ```


    **2. Place real data files** in the `data/` folder:
    ```
    data/
    ├── OpenPermID-bulk-currency.ntriples
    ├── OpenPermID-bulk-assetClass.ntriples
    ├── OpenPermID-bulk-industry.ntriples
    ├── OpenPermID-bulk-organization.ntriples
    ├── OpenPermID-bulk-person.ntriples
    ├── OpenPermID-bulk-quote.ntriples
    └── OpenPermID-bulk-instrument.ntriples
    ```

    **3. Run the app**
    ```bash
    streamlit run Home.py
    ```
    """
    )
