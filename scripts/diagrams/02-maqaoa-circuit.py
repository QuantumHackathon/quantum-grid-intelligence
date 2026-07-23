"""
Quantum Grid Intelligence — 02 MA-QAOA Circuit Architecture
Warm-start (Goemans-Williamson) → one representative layer (cost + mixer, repeated p×) → measurement.
Renders both horizontal (slide) and vertical (README/docs) orientations from one graph definition.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _style import *
import graphviz


def build(rankdir: str) -> graphviz.Digraph:
    is_h = rankdir == "LR"
    g = graphviz.Digraph("maqaoa-circuit")
    g.attr(**base_graph_attr(
        rankdir=rankdir,
        splines="spline",
        size="13,7" if is_h else "7.3,11",
        label=hl(
            "Multi-Angle Warm-Started QAOA",
            "per-edge γ · per-qubit β · bias-preserving mixer",
        ),
    ))
    g.attr("node", **base_node_attr())
    g.attr("edge", **base_edge_attr())

    with g.subgraph(name="cluster_warmstart") as w:
        w.attr(**cluster_attr("Warm Start", B_CLASSICAL))
        w.node("gw", hl("Goemans-Williamson SDP", "continuous relaxation"),
               fillcolor=F_CLASSICAL, color=B_CLASSICAL)
        w.node("init", hl("Warm-start prep", "Ry(θᵢ) from cᵢ per qubit"),
               fillcolor=F_CLASSICAL, color=B_CLASSICAL)

    with g.subgraph(name="cluster_layer") as l:
        l.attr(**cluster_attr("Layer l", B_QUANTUM, "repeated p times"))
        l.node("cost", hl("Cost Unitary", "U(H_C, γ) · per-edge γᵢⱼ"),
               fillcolor=F_QUANTUM, color=B_QUANTUM)
        l.node("mixer", hl("Mixer Unitary", "U(H_B, β) · per-qubit βᵢ"),
               fillcolor=F_QUANTUM, color=B_QUANTUM)

    g.node("measure", hl("Measurement", "bitstring x → Max-Cut value"),
           fillcolor=F_SUCCESS, color=B_SUCCESS)

    g.node("note", hl("Standard QAOA", "2 shared angles / layer", "MA-QAOA: m+n angles / layer"),
           fillcolor=F_DEFAULT, color=B_DEFAULT, fontsize="9", style="filled,dashed,rounded")

    g.edge("gw", "init", color=B_CLASSICAL)
    g.edge("init", "cost", color=B_QUANTUM, penwidth="2")
    g.edge("cost", "mixer", color=B_QUANTUM, penwidth="2")
    g.edge("mixer", "measure", color=B_SUCCESS, penwidth="2")
    g.edge("mixer", "cost", style="dashed", color=T_LITE, fontcolor=T_MED,
           label="×p layers", constraint="false")
    g.edge("note", "cost", style="dotted", color=T_LITE, arrowhead="none", constraint="false")

    return g


if __name__ == "__main__":
    render(build("LR"), "02-maqaoa-circuit", "docs/diagrams/output/horizontal")
    render(build("TB"), "02-maqaoa-circuit", "docs/diagrams/output/vertical")
