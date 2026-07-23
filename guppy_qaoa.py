#!/usr/bin/env python3
"""
Multi-Angle Warm-Started QAOA (MA-QAOA) in Guppy — for execution on Quantinuum Nexus
======================================================================================
Companion to quantum_grid_intelligence.py. Reuses the ICE grid graph, the
Goemans-Williamson warm-start probabilities (c_i), and the already-optimized
per-edge gamma / per-qubit beta angles from the NumPy MA-QAOA pipeline — but
expresses the circuit itself as a Guppy program compiled to HUGR, so it can
be executed for real on Quantinuum Nexus (Selene emulator) instead of an
idealized statevector.

quantum_grid_intelligence.optimize_qaoa() parameterizes MA-QAOA with an
independent gamma per edge and an independent beta per qubit (per layer),
not the two global angles of standard QAOA — this module mirrors that: each
layer applies a `zz_phase` per edge with its own gamma, and a bias-preserving
mixer per qubit with its own beta.

Nexus execute-jobs require a parameterless entrypoint (a closed circuit), so
all gamma/beta angles are baked in as compile-time constants here rather than
passed as runtime array arguments — the classical optimization already
happened in quantum_grid_intelligence.optimize_qaoa(); this module only
re-expresses the resulting fixed-angle circuit in Guppy.

Math note — bias-preserving mixer as native gates (per qubit i, per layer):
  H_B(c_i) = (2c_i-1) Z + (-2*sqrt(c_i(1-c_i))) X = cos(theta_i) Z + sin(theta_i) X
  with theta_i = atan2(-2*sqrt(c_i(1-c_i)), 2c_i-1) — depends only on c_i, so
  it is the same across layers; only beta varies per layer (and, under
  MA-QAOA, per qubit within a layer).
  Since a^2+b^2=1, H_B is a unit vector in the XZ-plane, so
    exp(-i*beta*H_B) = R_n(2*beta) = Ry(theta_i) . Rz(2*beta) . Ry(-theta_i)
  which is exact (no approximation) and uses only native single-qubit gates.

Run standalone (no Nexus needed, just checks + compiles locally):
    python guppy_qaoa.py
"""
import math

import numpy as np

from guppylang import guppy
from guppylang.std.angles import pi
from guppylang.std.builtins import array, py, result
from guppylang.std.quantum import qubit, ry, rz, measure_array
from guppylang.std.qsystem import zz_phase

from quantum_grid_intelligence import (
    NUM_QAOA_RUNS,
    SEED,
    brute_force_maxcut,
    goemans_williamson_maxcut,
    load_grid_graph,
    maxcut_value,
    optimize_qaoa,
)


def _rad_to_halfturns(rad):
    """Python-level radians -> guppy `angle` half-turn units (angle = halfturns * pi)."""
    return rad / math.pi


def compute_warm_start_c_i(G):
    """Reproduce the c_i warm-start probabilities exactly as in
    quantum_grid_intelligence.main() (Section: WS-QAOA Warm Start Integration)."""
    _, _, _, _, X_val = goemans_williamson_maxcut(G)
    nodes_list = list(G.nodes())
    c_i_list = []
    for idx, i in enumerate(nodes_list):
        c_val = (1 - X_val[0, idx]) / 2.0
        c_val = float(np.clip(c_val, 0.05, 0.95))
        c_i_list.append(c_val)
        G.nodes[i]["c_i"] = c_val  # qaoa_statevector() reads this back off G
    return c_i_list


def get_optimized_params(G, p=1, num_runs=NUM_QAOA_RUNS):
    """Run the existing MA-QAOA optimizer (L-BFGS-B) on the NumPy statevector
    simulator to get gamma*, beta* — the same procedure that produced the
    MA-QAOA headline result in quantum_grid_intelligence.py.

    optimize_qaoa() returns best_params as a flat array of length p*m + p*n
    (m edges, n nodes): p*m per-edge gammas followed by p*n per-qubit betas.
    Reshape it into what build_ws_qaoa_circuit expects: gamma_values[layer] is
    an array of m per-edge angles, beta_values[layer] is an array of n
    per-qubit angles.
    """
    n = G.number_of_nodes()
    m = G.number_of_edges()
    res = optimize_qaoa(G, p, num_runs=num_runs, verbose=False)
    best_params = np.asarray(res["best_params"])
    gamma_values = best_params[: p * m].reshape((p, m)).tolist()
    beta_values = best_params[p * m :].reshape((p, n)).tolist()
    return gamma_values, beta_values, res["best_cut"]


def build_ws_qaoa_circuit(G, c_i_list, gamma_values, beta_values):
    """Build a closed (parameterless) Guppy program for MA-QAOA (independent
    gamma per edge, independent beta per qubit, per layer) with all angles
    baked in as compile-time constants — required for Nexus, whose
    execute-jobs run a fixed circuit, not a runtime-parameterized one.

    gamma_values: length-p sequence, each an array/list of m per-edge angles
                  (edge order matches G.edges(data=True), same as
                  quantum_grid_intelligence.optimize_qaoa's internal edges_list).
    beta_values:  length-p sequence, each an array/list of n per-qubit angles.

    Returns the @guppy-decorated `main` function definition (not yet compiled).
    """
    p = len(gamma_values)
    assert len(beta_values) == p

    nodes_list = list(G.nodes())
    n = len(nodes_list)
    idx_of = {node: k for k, node in enumerate(nodes_list)}
    edges = [(idx_of[u], idx_of[v], float(data["weight"])) for u, v, data in G.edges(data=True)]
    m = len(edges)

    for layer_gammas, layer_betas in zip(gamma_values, beta_values):
        assert len(layer_gammas) == m, "gamma_values[layer] must have one angle per edge"
        assert len(layer_betas) == n, "beta_values[layer] must have one angle per qubit"

    # Mixer axis angle per qubit (half-turns), from H_B = cos(theta) Z + sin(theta) X.
    # Depends only on c_i, so it's the same across layers — only beta varies.
    theta_halfturns = [
        _rad_to_halfturns(math.atan2(-2 * math.sqrt(c * (1 - c)), 2 * c - 1))
        for c in c_i_list
    ]
    # Warm-start init angle per qubit (half-turns): |psi_i> = sqrt(1-c)|0> + sqrt(c)|1>
    init_halfturns = [_rad_to_halfturns(2 * math.asin(math.sqrt(c))) for c in c_i_list]

    # Guppy only auto-resolves closures wrapped in py(...), and only unrolls
    # `for x in py(<python list>)` loops at compile time. Crucially, a list
    # bound to an OUTER py(...) loop variable can't be fed into a nested
    # py(...) — once unrolled, that variable is a Guppy value, not a raw
    # Python object py() can re-evaluate. So instead of nesting a per-layer
    # loop inside a per-layer-list loop, every gate in the whole circuit
    # (across all layers, in the exact order they must execute) is flattened
    # into a single list of uniform (op_code, qubit_a, qubit_b, angle_halfturns)
    # tuples, iterated with ONE py(...) loop and dispatched with plain if/elif
    # — qubit_b is unused (0) for the single-qubit ops.
    qubit_inits = list(enumerate(init_halfturns))  # [(i, init_i), ...]

    ZZ_OP, RY_OP, RZ_OP = 0, 1, 2
    flat_ops = []
    for layer_gammas, layer_betas in zip(gamma_values, beta_values):
        # Cost unitary: ZZ interaction per edge, independent gamma per edge.
        # quantum_grid_intelligence.py applies U = exp(i*(gamma*w/2)*ZZ), but
        # guppy's zz_phase(theta) = exp(-i*theta/2*ZZ), so matching the two
        # requires theta = -(gamma*w).
        for idx, (u, v, w) in enumerate(edges):
            zz_ht = _rad_to_halfturns(-(float(layer_gammas[idx]) * w))
            flat_ops.append((ZZ_OP, u, v, zz_ht))

        # Bias-preserving mixer per qubit: R_n(2*beta_i) = Ry(theta_i) . Rz(2*beta_i) . Ry(-theta_i),
        # as a MATRIX PRODUCT, which means Ry(-theta_i) is applied FIRST in
        # circuit/temporal order and Ry(theta_i) LAST (matrix product order is
        # reversed from gate application order).
        for i in range(n):
            theta_ht = theta_halfturns[i]
            beta2_ht = _rad_to_halfturns(2.0 * float(layer_betas[i]))
            flat_ops.append((RY_OP, i, 0, -theta_ht))
            flat_ops.append((RZ_OP, i, 0, beta2_ht))
            flat_ops.append((RY_OP, i, 0, theta_ht))

    @guppy
    def main() -> None:
        qs = array(qubit() for _ in range(py(n)))

        # Warm-start state preparation: Ry(init_i) per qubit
        for i, init_ht in py(qubit_inits):
            ry(qs[i], init_ht * pi)

        for op_code, a, b, ang in py(flat_ops):
            if op_code == 0:
                zz_phase(qs[a], qs[b], ang * pi)
            elif op_code == 1:
                ry(qs[a], ang * pi)
            else:
                rz(qs[a], ang * pi)

        result("c", measure_array(qs))

    return main


def energy_from_counts(G, counts, n_shots):
    """Expected Max-Cut value from a {bitstring: count} distribution."""
    nodes_list = list(G.nodes())
    idx_of = {node: k for k, node in enumerate(nodes_list)}
    energy = 0.0
    for bits, count in counts.items():
        x = np.array([int(b) for b in bits])
        # counts are keyed in qubit order [q0, q1, ..., qn-1] == nodes_list order
        cut = 0.0
        for u, v, data in G.edges(data=True):
            if x[idx_of[u]] != x[idx_of[v]]:
                cut += data["weight"]
        energy += cut * (count / n_shots)
    return energy


if __name__ == "__main__":
    print("=" * 70)
    print("  MA-QAOA in Guppy — local build & compile check")
    print("=" * 70)

    np.random.seed(SEED)

    print("\nLoading ICE grid graph and computing GW warm-start probabilities...")
    G, _ = load_grid_graph()
    c_i_list = compute_warm_start_c_i(G)
    print(f"  c_i = {[round(c, 3) for c in c_i_list]}")

    optimal_cut, _ = brute_force_maxcut(G)
    print(f"  Brute-force optimal cut = {optimal_cut:.2f}")

    print("\nOptimizing per-edge gamma / per-qubit beta on the NumPy statevector simulator (p=1)...")
    gamma_values, beta_values, ideal_cut = get_optimized_params(G, p=1)
    for layer, (g_layer, b_layer) in enumerate(zip(gamma_values, beta_values)):
        print(f"  layer {layer}: gamma (per edge) = {[round(g, 4) for g in g_layer]}")
        print(f"  layer {layer}: beta  (per qubit) = {[round(b, 4) for b in b_layer]}")
    print(f"  Idealized statevector cut = {ideal_cut:.3f} (r = {ideal_cut / optimal_cut:.3f})")

    print(f"\nBuilding Guppy MA-QAOA circuit ({G.number_of_nodes()} qubits, p={len(gamma_values)})...")
    main = build_ws_qaoa_circuit(G, c_i_list, gamma_values, beta_values)

    print("Type-checking...")
    main.check()
    print("  OK")

    print("Compiling to HUGR...")
    hugr = main.compile()
    print(f"  OK — compiled package: {hugr}")
    print("\nThis HUGR package is ready to upload to Nexus with qnx.hugr.upload(...)")
    print("and execute with qnx.start_execute_job(..., backend_config=SeleneConfig()).")
