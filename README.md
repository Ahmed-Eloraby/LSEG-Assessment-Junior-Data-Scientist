# OpenPermID Graph Explorer

A Streamlit multi-page app for exploring OpenPermID financial knowledge graph data.

## Project Structure

```
openpermid_app/
├── Home.py                    ← App entry point (run this)
├── requirements.txt
├── data/                      ← Place your .ntriples files here
├── pages/
│   ├── 1_Currency.py          ← Q1
│   ├── 2_Asset_Class.py       ← Q2
│   ├── 3_Industry.py          ← Q3 (includes network diagram)
│   ├── 4_Organization.py      ← Q4
│   ├── 5_Person.py            ← Q5
│   ├── 6_Quote.py             ← Q6
│   └── 7_Instrument.py        ← Q7
└── utils/
    ├── parser.py              ← Shared N-Triples parser
    ├── graph_viz.py           ← PyVis network builder
    ├── ui.py                  ← Theme, CSS, shared components
    └── generate_demo_data.py  ← Synthetic demo data generator
```

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2a. Use demo data (no real files needed)
```bash
python utils/generate_demo_data.py
```

### 2b. Use real OpenPermID data
Extract your `.gz` files into the `data/` folder:
```bash
gunzip -k OpenPermID-bulk-*.ntriples.gz
mv OpenPermID-bulk-*.ntriples data/
```
Both `.ntriples` and `.ntriples.gz` are supported — the parser handles both automatically.

### 3. Run the app
```bash
streamlit run Home.py
```

## Key Design Decisions

| Choice | Why |
|--------|-----|
| `rdflib` for parsing | Native N-Triples support, handles URIs and literals correctly |
| `pandas` for analysis | Everything becomes `groupby` / `value_counts` |
| `plotly` for charts | Interactive, dark-theme friendly, embeds natively in Streamlit |
| `pyvis` for network | Renders interactive HTML graphs, embeddable via `components.html()` |
| No Neo4j | Assessment questions are exploratory/analytical — no graph queries needed |
| `@st.cache_data` | Prevents re-parsing on every Streamlit re-render |
