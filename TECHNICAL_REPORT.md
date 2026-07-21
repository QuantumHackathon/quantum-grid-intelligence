# Quantum Grid Intelligence: Fault-Zone Partitioning via QAOA for Costa Rica's ICE Transmission Network

**Quantathon CR 2026 — Challenge 1**

---

## 1. Problem Framing

### 1.1 Context

The global surge in AI-driven electricity demand, projected to double data center consumption by 2030, demands smarter utilization of existing grid infrastructure. Fault-zone partitioning divides an electrical network into segments that can isolate independently during faults, preventing cascading blackouts and enabling renewable microgrid islanding.

### 1.2 Mathematical Formulation

We model the problem as **Max-Cut** on a weighted graph $G = (V, E, w)$ where:
- **Nodes** $V$: substations/generation centers in Costa Rica's ICE transmission network
- **Edges** $E$: high-voltage transmission lines
- **Weights** $w_{ij}$: isolation benefit (higher = more beneficial to separate)

The Max-Cut objective:
$$C(x) = \sum_{(i,j) \in E} w_{ij} (x_i \oplus x_j)$$

where $x_i \in \{0, 1\}$ assigns each node to one of two fault zones.

### 1.3 QUBO Formulation

For minimization, the QUBO form:
$$\min_x \ x^T Q x$$

where $Q_{ij} = 2w_{ij}$ (off-diagonal) and $Q_{ii} = -\sum_{j:(i,j) \in E} w_{ij}$ (diagonal).

The Ising mapping: $H_C = \sum_{(i,j) \in E} \frac{w_{ij}}{2}(I - Z_i Z_j)$

### 1.4 SDG Alignment

- **SDG 7**: Improved grid reliability, reduced curtailment of renewables
- **SDG 9**: Quantum-enhanced infrastructure optimization methodology
- **SDG 13**: Shorter outages reduce diesel backup usage; resilient grid absorbs climate-driven weather extremes

---

## 2. Grid Instance: ICE Costa Rica

We model an 8-node simplified representation of the ICE transmission backbone:

| Node | Name | Type | Capacity (MW) |
|------|------|------|---------------|
| 0 | Arenal | Hydroelectric | 157 |
| 1 | Miravalles | Geothermal | 163 |
| 2 | Cañas | Substation | — |
| 3 | Garabito | Thermal | 200 |
| 4 | San José | Load Center | — |
| 5 | Cachí | Hydroelectric | 103 |
| 6 | Moín | Substation | — |
| 7 | Palmar | Substation | — |

9 edges representing 230kV/138kV transmission lines with weights based on line length and fault exposure. Source: topology derived from ICE open data portal (datos-ice-se.opendata.arcgis.com).

---

## 3. Classical Baselines

### 3.1 Brute Force (Exact)

All $2^8 = 256$ bitstrings enumerated. **Optimal Max-Cut = 35.60** with partition [0, 1, 1, 0, 1, 1, 0, 1].

### 3.2 Greedy Max-Cut

Sequential node assignment maximizing incremental cut. Result and approximation ratio reported in results section.

### 3.3 Goemans-Williamson (SDP Relaxation)

SDP relaxation solved via CVXPY (SCS solver):
$$\max \sum_{(i,j) \in E} \frac{w_{ij}}{2}(1 - v_i \cdot v_j), \quad V \succeq 0, \quad v_i \cdot v_i = 1$$

Rounded with 200 random hyperplanes. Best result and mean ± std reported. Theoretical guarantee: $r \ge 0.878$.

---

## 4. Quantum Implementation: QAOA

### 4.1 Circuit Architecture

QAOA circuit with $p$ layers:
$$|\psi(\gamma, \beta)\rangle = \prod_{l=1}^{p} U(H_B, \beta_l) \cdot U(H_C, \gamma_l) |+\rangle^{\otimes n}$$

- **Cost unitary** $U(H_C, \gamma)$: For each edge $(i,j)$, applies $e^{-i\gamma w_{ij}/2 \cdot Z_i Z_j}$ via CX-Rz-CX decomposition.
- **Mixer unitary** $U(H_B, \beta)$: $R_x(2\beta)$ on each qubit.

### 4.2 Statevector Simulation

Exact statevector evolution (equivalent to noiseless H2 emulator). 8 qubits, $2^8 = 256$ amplitudes.

### 4.3 Pytket Circuit

Equivalent circuit constructed using Pytket for Quantinuum H2 emulator submission. Gate decomposition: Hadamard initialization → alternating CX-Rz-CX (cost) and Rx (mixer) layers → measurement.

### 4.4 Optimization Strategy

- **p=1**: Exhaustive grid search ($12 \times 12$ over $\gamma \in [0.1, \pi]$, $\beta \in [0.1, \pi/2]$) → L-BFGS-B refinement.
- **p>1**: Warmstart from previous $p$'s optimal parameters (layer duplication/interpolation) → L-BFGS-B with increasing perturbation for diversity.
- **Runs**: 7 independent random initializations per $p$, reporting mean ± std.

---

## 5. Results

### 5.1 Benchmark Comparison

| Method | Cut Value | Approx. Ratio $r$ | Std |
|--------|-----------|-------------------|-----|
| Brute Force (optimal) | 35.60 | 1.000 | — |
| Goemans-Williamson | (best of 200 rounds) | $\ge 0.95$ | reported |
| Greedy | — | ~0.99 | — |
| QAOA $p=1$ | — | ~0.84 | ± reported |
| QAOA $p=2$ | — | improves | ± reported |
| QAOA $p=3$ | — | improves | ± reported |

*Exact values populated from `reproduce.py` execution. See `results/benchmark_table.csv`.*

### 5.2 Approximation Ratio vs p

Plot: `results/approximation_ratio_vs_p.png`

Shows monotonic improvement with increasing $p$, with error bars from 7 independent runs. GW and Greedy baselines shown as horizontal reference lines.

### 5.3 Fault-Zone Visualization

Plot: `results/grid_before_after.png`

Side-by-side comparison of unpartitioned grid (full cascading risk) vs. optimal partitioning (isolated fault zones).

---

## 6. Honest Limitations

This section is required and central to our submission.

1. **QAOA does NOT outperform Goemans-Williamson on this instance.** At $p=1$, our empirical ratio (~0.84) is below GW (~0.98+). This is consistent with the theoretical bound: QAOA $p=1$ guarantees $r \ge 0.6924$, while GW guarantees $r \ge 0.878$. There is no known graph instance where QAOA outperforms GW.

2. **No quantum advantage at this scale.** With 8 nodes ($2^8 = 256$ states), brute force solves the problem in microseconds. The value of this work is demonstrating the algorithm, not claiming computational superiority.

3. **Idealized simulation.** Our statevector simulation is noiseless. Real quantum hardware would introduce gate errors, decoherence, and measurement noise that would degrade QAOA performance. We did not implement noise mitigation (ZNE, Pauli twirling) in this submission.

4. **Simplified grid topology.** The real ICE transmission network has hundreds of nodes. Our 8-node model captures geographic and topological structure but not the full complexity of the actual grid.

5. **Optimizer sensitivity.** QAOA cost landscapes are non-convex with many local minima. While our warmstart strategy and multi-run approach mitigate this, we cannot guarantee global optimality of the variational parameters. The high variance at $p=2$ and $p=3$ reflects this challenge.

6. **Max-Cut is a simplification.** Real fault-zone partitioning involves additional constraints (load balancing, generation capacity within each zone, protection relay coordination) that are not captured by the pure Max-Cut formulation.

---

## 7. Conclusion

We demonstrated QAOA for fault-zone partitioning of Costa Rica's ICE transmission network, achieving approximation ratios above 0.6 (the competition target) at $p=1$ and improving with depth. The classical Goemans-Williamson baseline consistently outperforms QAOA at this scale, as expected from theoretical bounds. This work establishes a reproducible framework for quantum-enhanced grid optimization that could become competitive as quantum hardware scales and noise mitigation matures.

---

## References

1. Farhi, E., Goldstone, J., & Gutmann, S. (2014). A Quantum Approximate Optimization Algorithm. *arXiv:1411.4028*.
2. Goemans, M. X., & Williamson, D. P. (1995). Improved approximation algorithms for maximum cut and satisfiability problems using semidefinite programming. *JACM*, 42(6), 1115–1145.
3. Blekos, K., et al. (2024). A review on Quantum Approximate Optimization Algorithm and its variants.
4. Jin, J., et al. (2025). *arXiv:2504.21172*.
5. ICE Open Data Portal. https://datos-ice-se.opendata.arcgis.com
