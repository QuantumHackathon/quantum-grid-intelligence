"""
Quantum Grid Intelligence — 01 Pipeline Overview
Hero diagram: grid data → graph → QUBO/Ising → classical + quantum solve → partition → real execution.
Renders both horizontal (slide) and vertical (README/docs) orientations from one graph definition.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _style import *
import graphviz


def build(rankdir: str) -> graphviz.Digraph:
    is_h = rankdir == "LR"
    g = graphviz.Digraph("pipeline-overview")
    g.attr(**base_graph_attr(
        rankdir=rankdir,
        splines="spline",
        size="13,7" if is_h else "7.3,11",
        label=hl(
            "Quantum Grid Intelligence — Pipeline",
            "ICE Costa Rica transmission network · fault-zone partitioning as Max-Cut",
        ),
    ))
    g.attr("node", **base_node_attr())
    g.attr("edge", **base_edge_attr())

    g.node("data", hl("Power Grid Data", "ice_grid_topology.json", "8 nodes · 9 weighted edges"),
           fillcolor=F_LOAD, color=B_DEFAULT)

    with g.subgraph(name="cluster_classical") as c:
        c.attr(**cluster_attr("Problem Formulation", B_CLASSICAL))
        c.node("graph", hl("Weighted Graph", "substations · transmission lines"),
               fillcolor=F_CLASSICAL, color=B_CLASSICAL)
        c.node("qubo", hl("QUBO / Ising", "Max-Cut objective"),
               fillcolor=F_CLASSICAL, color=B_CLASSICAL)

    g.node("classical", hl("Classical Baselines", "Brute Force · Greedy · Goemans-Williamson"),
           fillcolor=F_CLASSICAL, color=B_CLASSICAL)

    with g.subgraph(name="cluster_quantum") as q:
        q.attr(**cluster_attr("Quantum-Hybrid Optimization", B_QUANTUM))
        q.node("maqaoa", hl("MA-QAOA", "warm-started · multi-angle"),
               fillcolor=F_QUANTUM, color=B_QUANTUM)
        q.node("partition", hl("Optimal Partition", "fault-isolated zones"),
               fillcolor=F_SUCCESS, color=B_SUCCESS)

    with g.subgraph(name="cluster_execution") as e:
        e.attr(**cluster_attr("Real Execution", B_EXEC))
        e.node("guppy", hl("Guppy → HUGR", "gate-level compile"),
               fillcolor=F_EXEC, color=B_EXEC)
        e.node("nexus", hl("Quantinuum Nexus", "Selene emulator · 5000 shots"),
               fillcolor=F_EXEC, color=B_EXEC)

    g.edge("data", "graph")
    g.edge("graph", "qubo")
    g.edge("qubo", "classical", label="classical solve", color=B_CLASSICAL, fontcolor=B_CLASSICAL)
    g.edge("qubo", "maqaoa", label="quantum solve", color=B_QUANTUM, fontcolor=B_QUANTUM, penwidth="2")
    g.edge("classical", "partition", style="dashed", color=B_CLASSICAL, label="benchmark")
    g.edge("maqaoa", "partition", color=B_QUANTUM, penwidth="2")
    g.edge("partition", "guppy", color=B_EXEC, penwidth="2")
    g.edge("guppy", "nexus", color=B_EXEC, penwidth="2")

    return g


if __name__ == "__main__":
    render(build("LR"), "01-pipeline-overview", "docs/diagrams/output/horizontal")
    render(build("TB"), "01-pipeline-overview", "docs/diagrams/output/vertical")
