"""
Quantum Grid Intelligence — 03 Benchmark Method Tree
Classical baselines vs. quantum-hybrid MA-QAOA, both branching from the Max-Cut problem.
Horizontal: two parallel columns. Vertical: classical block stacked above quantum block
(forced via an invisible ranking edge) instead of one wide row of 5 leaves.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _style import *
import graphviz


def build(rankdir: str) -> graphviz.Digraph:
    is_h = rankdir == "LR"
    g = graphviz.Digraph("benchmark-tree")
    g.attr(**base_graph_attr(
        rankdir=rankdir,
        splines="spline",
        size="13,7" if is_h else "7.3,11",
        label=hl(
            "Classical vs. Quantum-Hybrid Benchmark",
            "Fault-Zone Partitioning (Max-Cut) on the 8-node ICE grid",
        ),
    ))
    g.attr("node", **base_node_attr())
    g.attr("edge", **base_edge_attr())

    g.node("root", hl("Fault-Zone Partitioning", "Max-Cut"), fillcolor=F_DEFAULT, color=B_DEFAULT)

    with g.subgraph(name="cluster_classical") as c:
        c.attr(**cluster_attr("Classical Baselines", B_CLASSICAL))
        c.node("bf", hl("Brute Force", "exact · r = 1.000"), fillcolor=F_CLASSICAL, color=B_CLASSICAL)
        c.node("gw", hl("Goemans-Williamson", "SDP · r ≥ 0.878"), fillcolor=F_CLASSICAL, color=B_CLASSICAL)
        c.node("greedy", hl("Greedy", "heuristic · r ≈ 0.5"), fillcolor=F_CLASSICAL, color=B_CLASSICAL)

    with g.subgraph(name="cluster_quantum") as q:
        q.attr(**cluster_attr("Quantum-Hybrid", B_QUANTUM))
        q.node("maqaoa", hl("MA-QAOA p=1", "idealized · r ≈ 0.987"), fillcolor=F_QUANTUM, color=B_QUANTUM)
        q.node("maqaoa_nexus", hl("MA-QAOA on Nexus", "Selene, 5000 shots · r ≈ 0.987"),
               fillcolor=F_QUANTUM, color=B_QUANTUM)

    g.edge("root", "bf", color=B_CLASSICAL)
    g.edge("root", "gw", color=B_CLASSICAL)
    g.edge("root", "greedy", color=B_CLASSICAL)
    g.edge("root", "maqaoa", color=B_QUANTUM, penwidth="2")
    g.edge("maqaoa", "maqaoa_nexus", color=B_QUANTUM, label="same circuit,\nreal execution")

    if not is_h:
        # Force the quantum cluster to a later rank than the classical cluster so it
        # stacks below (tall column) instead of sharing one wide row of 5 leaves.
        g.edge("greedy", "maqaoa", style="invis", constraint="true")

    return g


if __name__ == "__main__":
    render(build("LR"), "03-benchmark-tree", "docs/diagrams/output/horizontal")
    render(build("TB"), "03-benchmark-tree", "docs/diagrams/output/vertical")
