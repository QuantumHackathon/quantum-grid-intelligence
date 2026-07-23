#!/usr/bin/env python3
"""
Execute the WS-QAOA circuit (built in guppy_qaoa.py) on Quantinuum Nexus.

Requires an authenticated Nexus session (run `qnx.login()` once beforehand).
Uploads the compiled HUGR to a Nexus project and executes it on the
Nexus-hosted Selene emulator (noiseless statevector simulator), then compares
the shot-based empirical cut value against the idealized NumPy statevector
result.

Run: python run_on_nexus.py
"""
import csv

import numpy as np
import qnexus as qnx
from quantinuum_schemas.models.backend_config import SeleneConfig

from quantum_grid_intelligence import RESULTS_DIR, SEED, brute_force_maxcut, load_grid_graph
from guppy_qaoa import (
    build_ws_qaoa_circuit,
    compute_warm_start_c_i,
    energy_from_counts,
    get_optimized_params,
)

PROJECT_NAME = "quantum-grid-intelligence"
N_SHOTS = 5000


def append_nexus_row_to_benchmark_csv(cut, ratio, n_shots):
    """Add/replace the Nexus execution row in results/benchmark_table.csv,
    which quantum_grid_intelligence.py otherwise only populates with
    NumPy-simulated rows."""
    csv_path = RESULTS_DIR / "benchmark_table.csv"
    fieldnames = ["Method", "Cut Value", "Approx Ratio", "Std", "Partition"]

    with open(csv_path, newline="") as f:
        rows = [row for row in csv.DictReader(f) if not row["Method"].startswith("WS-QAOA p=1 (Nexus")]

    rows.append({
        "Method": f"WS-QAOA p=1 (Nexus Selene, {n_shots} shots)",
        "Cut Value": f"{cut:.2f}",
        "Approx Ratio": f"{ratio:.3f}",
        "Std": "shot noise only",
        "Partition": "—",
    })

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    np.random.seed(SEED)

    print("Loading ICE grid graph and computing GW warm-start probabilities...")
    G, _ = load_grid_graph()
    c_i_list = compute_warm_start_c_i(G)
    optimal_cut, _ = brute_force_maxcut(G)

    print("Optimizing gamma/beta on the NumPy statevector simulator (p=1)...")
    gamma_values, beta_values, ideal_cut = get_optimized_params(G, p=1)
    ideal_ratio = ideal_cut / optimal_cut
    print(f"  gamma={gamma_values}, beta={beta_values}")
    print(f"  Idealized statevector cut = {ideal_cut:.3f} (r = {ideal_ratio:.3f})")

    print("\nBuilding and compiling the Guppy WS-QAOA circuit...")
    circuit = build_ws_qaoa_circuit(G, c_i_list, gamma_values, beta_values)
    circuit.check()
    hugr = circuit.compile()
    print("  OK")

    print(f"\nConnecting to Nexus project '{PROJECT_NAME}'...")
    project = qnx.projects.get_or_create(name=PROJECT_NAME)

    print("Uploading HUGR...")
    hugr_ref = qnx.hugr.upload(
        hugr_package=hugr,
        name="ws-qaoa-p1-ice-grid",
        project=project,
    )
    print(f"  Uploaded: {hugr_ref}")

    print(f"\nSubmitting execute job to Nexus Selene emulator ({N_SHOTS} shots)...")
    backend_config = SeleneConfig()
    job_ref = qnx.start_execute_job(
        programs=[hugr_ref],
        n_shots=[N_SHOTS],
        backend_config=backend_config,
        project=project,
        name="ws-qaoa-p1-execute",
        n_qubits=[G.number_of_nodes()],
    )
    print(f"  Job submitted: {job_ref}")

    print("Waiting for job completion...")
    qnx.jobs.wait_for(job_ref)

    result_ref = qnx.jobs.results(job_ref)[0]
    qsys_result = result_ref.download_result()
    counts = qsys_result.register_counts()["c"]

    print("\n" + "=" * 70)
    print("  RESULTS: Nexus Selene emulator execution")
    print("=" * 70)
    total = sum(counts.values())
    print(f"  Distinct bitstrings observed: {len(counts)} (out of {N_SHOTS} shots)")

    empirical_cut = energy_from_counts(G, counts, total)
    empirical_ratio = empirical_cut / optimal_cut

    print(f"\n  Optimal (brute force)          cut = {optimal_cut:.3f}  r = 1.000")
    print(f"  WS-QAOA idealized (statevector) cut = {ideal_cut:.3f}  r = {ideal_ratio:.3f}")
    print(f"  WS-QAOA Nexus (Selene, {N_SHOTS} shots) cut = {empirical_cut:.3f}  r = {empirical_ratio:.3f}")
    print(f"\n  Deviation from idealized: {abs(empirical_cut - ideal_cut):.4f}")

    append_nexus_row_to_benchmark_csv(empirical_cut, empirical_ratio, N_SHOTS)
    print(f"  Updated results/benchmark_table.csv with the Nexus row.")


if __name__ == "__main__":
    main()
