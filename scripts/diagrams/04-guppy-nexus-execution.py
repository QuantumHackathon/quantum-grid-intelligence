"""
Quantum Grid Intelligence — 04 Guppy → HUGR → Nexus Execution Flow
Optimized circuit is re-expressed in Guppy, compiled to HUGR, and executed on Quantinuum Nexus (Selene).
Renders both horizontal (slide) and vertical (README/docs) orientations from one graph definition.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _style import *
import graphviz


def build(rankdir: str) -> graphviz.Digraph:
    is_h = rankdir == "LR"
    g = graphviz.Digraph("guppy-nexus-execution")
    g.attr(**base_graph_attr(
        rankdir=rankdir,
        splines="spline",
        size="13,7" if is_h else "7.3,11",
        label=hl(
            "Real Execution on Quantinuum Nexus",
            "guppy_qaoa.py → run_on_nexus.py",
        ),
    ))
    g.attr("node", **base_node_attr())
    g.attr("edge", **base_edge_attr())

    with g.subgraph(name="cluster_build") as b:
        b.attr(**cluster_attr("Circuit Build", B_EXEC, "guppy_qaoa.py · local"))
        b.node("params", hl("Optimized γ*, β*", "NumPy statevector result"),
               fillcolor=F_QUANTUM, color=B_QUANTUM)
        b.node("guppy", hl("Guppy Circuit", "Ry warm-start · zz_phase · Ry-Rz-Ry mixer"),
               fillcolor=F_EXEC, color=B_EXEC)
        b.node("hugr", hl("compile() → HUGR", "Quantinuum IR"),
               fillcolor=F_EXEC, color=B_EXEC)

    with g.subgraph(name="cluster_nexus") as n:
        n.attr(**cluster_attr("Quantinuum Nexus", B_EXEC, "run_on_nexus.py · Selene emulator"))
        n.node("upload", hl("hugr.upload", "project: quantum-grid-intelligence"),
               fillcolor=F_EXEC, color=B_EXEC)
        n.node("job", hl("Execute Job", "SeleneConfig · 5000 shots"),
               fillcolor=F_EXEC, color=B_EXEC)
        n.node("counts", hl("Measurement Counts", "register \"c\" → energy_from_counts"),
               fillcolor=F_EXEC, color=B_EXEC)

    g.node("compare", hl("r = 0.987 ≈ 0.987", "idealized vs. Nexus, agree within shot noise"),
           fillcolor=F_SUCCESS, color=B_SUCCESS)

    g.edge("params", "guppy", color=B_EXEC)
    g.edge("guppy", "hugr", color=B_EXEC, penwidth="2")
    g.edge("hugr", "upload", color=B_EXEC, penwidth="2")
    g.edge("upload", "job", color=B_EXEC)
    g.edge("job", "counts", color=B_EXEC)
    g.edge("counts", "compare", color=B_SUCCESS, penwidth="2")
    g.edge("params", "compare", style="dashed", color=T_LITE, label="idealized ratio", constraint="false")

    return g


if __name__ == "__main__":
    render(build("LR"), "04-guppy-nexus-execution", "docs/diagrams/output/horizontal")
    render(build("TB"), "04-guppy-nexus-execution", "docs/diagrams/output/vertical")
