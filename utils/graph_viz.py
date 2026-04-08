"""
Network graph builder using PyVis + NetworkX.
Embeddable in Streamlit via st.components.v1.html().
"""

import networkx as nx
import streamlit.components.v1 as components


def build_network_html(
    edges: list[tuple[str, str, str]],
    max_nodes: int = 120,
    height: str = "520px",
    physics: bool = True,
) -> str:
    """
    Build a PyVis HTML string from a list of (subject, predicate, object) tuples.

    Parameters
    ----------
    edges      : list of (subject, predicate, object) strings
    max_nodes  : cap to keep the browser happy
    height     : iframe height string
    physics    : enable PyVis physics simulation
    """
    try:
        from pyvis.network import Network
    except ImportError:
        return "<p style='color:red'>Install pyvis: <code>pip install pyvis</code></p>"

    # Build networkx graph first for analysis
    G = nx.DiGraph()
    for s, p, o in edges[: max_nodes * 4]:
        G.add_node(s)
        G.add_node(o)
        G.add_edge(s, o, label=p)

    # Trim to max_nodes by degree (keep most-connected)
    if G.number_of_nodes() > max_nodes:
        top = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:max_nodes]
        keep = {n for n, _ in top}
        G = G.subgraph(keep).copy()

    net = Network(
        height=height,
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="#e0e0e0",
    )
    net.toggle_physics(physics)

    # Color nodes by rough type
    def node_color(name: str) -> str:
        name_l = name.lower()
        # if any(k in name_l for k in ["sector", "industry"]):
        #     return "#f97316"  # orange
        # if any(k in name_l for k in ["org", "company", "corp"]):
        #     return "#3b82f6"  # blue
        # if any(k in name_l for k in ["person", "ceo", "chair"]):
        #     return "#22c55e"  # green
        # if any(k in name_l for k in ["currency", "usd", "eur"]):
        #     return "#a855f7"  # purple
        # if any(k in name_l for k in ["inst", "bond", "equity"]):
        #     return "#06b6d4"  # cyan
        # if any(k in name_l for k in ["quote"]):
        #     return "#f59e0b"  # amber
        return "#94a3b8"  # slate default

    for node in G.nodes():
        net.add_node(
            node,
            label=node[:28],
            color=node_color(node),
            title=node,
            size=12 + min(G.degree(node) * 2, 20),
        )

    for s, o, data in G.edges(data=True):
        net.add_edge(s, o, label=data.get("label", ""), color="#475569", arrows="to")

    # Minimal options JSON
    net.set_options(
        """
    {
      "nodes": {"font": {"size": 11, "color": "#e2e8f0"}},
      "edges": {"font": {"size": 9, "color": "#94a3b8"}, "smooth": {"type": "curvedCW", "roundness": 0.2}},
      "physics": {"stabilization": {"iterations": 150}},
      "interaction": {"hover": true, "tooltipDelay": 100}
    }
    """
    )

    return net.generate_html()


def render_network(edges, max_nodes=120, height=520, physics=True):
    """Render the network inline in a Streamlit page."""
    html = build_network_html(
        edges, max_nodes=max_nodes, height=f"{height}px", physics=physics
    )
    components.html(html, height=height + 10, scrolling=False)
