"""
Quantum Grid Intelligence — 05 Grid Topology Schematic
Conceptual (non-geographic-map) 8-node ICE grid, colored by generation type, with the
optimal fault-zone cut [0,1,1,0,1,1,0,1] highlighted on the edges that cross it.

This diagram deliberately does NOT use graphviz's automatic hierarchical (dot) or
force-directed (neato spring-model) layout: the grid is a non-hierarchical mesh (it has
cycles), so `dot`+rankdir gives an arbitrary layered result, and unconstrained neato can
produce crossing edges that hurt legibility at this small size. Instead every node is
pinned (`pos=".."`, `pin=true`) to a position derived from its real lat/lon (normalized,
NOT to scale, NOT plotted on a map) — this keeps the topology recognizable and
edge-crossing-free while staying visually distinct from the geographic matplotlib plots
in results/. Orientation is controlled by scaling the x/y axes independently per call
(wide canvas for slides, tall canvas for docs), not by a rankdir flag — hence
`build(orientation)` takes "wide"/"tall", unlike the rankdir-based scripts.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _style import *
import graphviz

# id: (name, type, normalized_x, normalized_y)  — nx/ny derived from lon/lat, normalized to [0,1]
NODES = {
    0: ("Arenal",      "hydroelectric", 0.220, 0.836),
    1: ("Miravalles",  "geothermal",    0.000, 1.000),
    2: ("Cañas",       "substation",    0.047, 0.824),
    3: ("Garabito",    "thermal",       0.263, 0.562),
    4: ("San José",    "load_center",   0.524, 0.547),
    5: ("Cachí",       "hydroelectric", 0.655, 0.493),
    6: ("Moín",        "substation",    1.000, 0.587),
    7: ("Palmar",      "substation",    0.817, 0.000),
}

EDGES = [
    (0, 1, 4.2), (0, 2, 3.8), (1, 2, 3.5), (2, 3, 5.1), (3, 4, 6.3),
    (4, 5, 4.7), (5, 6, 5.8), (4, 6, 4.9), (3, 7, 5.5),
]

# Optimal partition (Brute Force, [0,1,1,0,1,1,0,1]) — side 0: Arenal/Garabito/Moín
PARTITION_SIDE0 = {0, 3, 6}

TYPE_STYLE = {
    "hydroelectric": (F_HYDRO, B_GRID),
    "geothermal":    (F_GEOTHERMAL, B_GRID),
    "thermal":       (F_THERMAL, B_GRID),
    "substation":    (F_SUBSTATION, B_SUBSTATION),
    "load_center":   (F_LOAD, B_GRID),
}


def build(orientation: str) -> graphviz.Graph:
    is_wide = orientation == "wide"
    kx, ky = (9.5, 5.2) if is_wide else (5.6, 8.5)

    g = graphviz.Graph("grid-topology-schematic", engine="neato")
    g.attr(**base_graph_attr(
        label=hl(
            "ICE Grid — Conceptual Topology & Optimal Fault-Zone Cut",
            "colored by generation type · red = edges crossing the optimal partition",
        ),
    ))
    g.attr("node", **base_node_attr())
    g.attr("edge", **base_edge_attr())
    g.attr(overlap="false", splines="line")

    for nid, (name, ntype, nx, ny) in NODES.items():
        fill, border = TYPE_STYLE[ntype]
        x_pt, y_pt = nx * kx * 72, ny * ky * 72
        g.node(
            str(nid), hl(name, ntype.replace("_", " ")),
            pos=f"{x_pt},{y_pt}!", pin="true",
            fillcolor=fill, color=border,
        )

    for a, b, w in EDGES:
        crosses = (a in PARTITION_SIDE0) != (b in PARTITION_SIDE0)
        penwidth = 1.4 + (w - 3.5) / (6.3 - 3.5) * 2.2
        if crosses:
            g.edge(str(a), str(b), color=E_FAULT, style="dashed", penwidth=f"{penwidth:.1f}")
        else:
            g.edge(str(a), str(b), color=E_DEFAULT, style="solid", penwidth=f"{penwidth:.1f}")

    return g


if __name__ == "__main__":
    render(build("wide"), "05-grid-topology-schematic", "docs/diagrams/output/horizontal")
    render(build("tall"), "05-grid-topology-schematic", "docs/diagrams/output/vertical")
