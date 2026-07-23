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
$$|\psi(\vec{\Gamma}, \vec{B})\rangle = \prod_{l=1}^{p} U(H_B, \vec{\beta}_l) \cdot U(H_C, \vec{\gamma}_l) |\psi_0\rangle$$

where, under **Multi-Angle QAOA (MA-QAOA)**, $\vec{\gamma}_l \in \mathbb{R}^m$ carries an independent angle per edge and $\vec{\beta}_l \in \mathbb{R}^n$ an independent angle per qubit — not the two global scalars $(\gamma_l, \beta_l)$ of standard QAOA.

- **Cost unitary** $U(H_C, \vec{\gamma})$: for each edge $(i,j)$, applies $e^{-i\gamma_{ij} w_{ij}/2 \cdot Z_i Z_j}$ via CX-Rz-CX decomposition, with its own $\gamma_{ij}$.
- **Mixer unitary** $U(H_B, \vec{\beta})$: standard QAOA uses a single $R_x(2\beta)$ on every qubit, initialized from $|+\rangle^{\otimes n}$. Our production version instead combines **warm-starting** with **multi-angle parameterization**, described below.

#### Multi-Angle Warm-Started QAOA (MA-QAOA)

Standard QAOA at $p=1$ has a theoretical guarantee ($r \ge 0.6924$) strictly below Goemans-Williamson's ($r \ge 0.878$). We close part of that gap with two combined ideas. First, **warm-starting**: each qubit $i$ is initialized to $|\psi_0\rangle_i = \sqrt{1-c_i}|0\rangle + \sqrt{c_i}|1\rangle$, where $c_i$ is derived from the continuous Goemans-Williamson SDP solution rather than from a uniform superposition. The mixer is correspondingly replaced by a **bias-preserving** Hamiltonian per qubit, $H_B(c_i) = (2c_i-1)Z + (-2\sqrt{c_i(1-c_i)})X$, whose ground state is exactly $|\psi_0\rangle_i$ — so the mixer alone leaves the warm-start bias untouched, and only the interleaved cost unitary moves the state away from it. Second, **multi-angle parameterization**: instead of one $\beta_l$ shared by every qubit's mixer and one $\gamma_l$ shared by every edge's cost term, each qubit $i$ gets its own $\beta_{i,l}$ and each edge $(i,j)$ its own $\gamma_{ij,l}$, per layer.

On the 8-node grid ($n=8$ qubits, $m=9$ edges), this gives $p \cdot (m+n) = 17p$ free classical parameters — 17 at $p=1$, 34 at $p=2$, 51 at $p=3$ — optimized against the idealized statevector simulator. See §6.2 for why that parameter count matters when interpreting the results.

### 4.2 Statevector Simulation

Exact statevector evolution (equivalent to noiseless H2 emulator). 8 qubits, $2^8 = 256$ amplitudes.

### 4.3 Pytket Circuit

Equivalent circuit constructed using Pytket for Quantinuum H2 emulator submission. Gate decomposition: Hadamard initialization → alternating CX-Rz-CX (cost) and Rx (mixer) layers → measurement. This circuit was constructed but not executed on hardware or emulator (see §4.5 for the circuit that was).

### 4.4 Real Execution on Quantinuum Nexus

The results in §4.1–4.3 come from an idealized, noiseless NumPy statevector simulation. To validate the circuit on genuine Quantinuum execution infrastructure rather than only a hand-rolled simulator, the optimized MA-QAOA $p=1$ circuit was re-expressed in **Guppy** — Quantinuum's Python-embedded, statically-typed quantum language — compiled to **HUGR** (Quantinuum's intermediate representation), and executed on **Quantinuum Nexus** against the Nexus-hosted **Selene emulator** (`SeleneConfig`, a noiseless statevector backend reached via genuine shot-based execution: `qnx.hugr.upload` → `qnx.start_execute_job` → 5000 shots → measurement counts).

**Gate-level translation.** The warm-start preparation becomes $R_y(\theta_i^{\text{init}})$ per qubit, with $\theta_i^{\text{init}} = 2\arcsin(\sqrt{c_i})$. The cost unitary maps to Guppy's native `zz_phase` gate, applied once per edge with **that edge's own** $\gamma_{ij}$: $\text{zz\_phase}(\theta_{ij}) = e^{-i\theta_{ij}/2 \cdot Z\otimes Z}$, with $\theta_{ij} = -\gamma_{ij} w_{ij}$ (sign and factor-of-two differ from the NumPy convention $e^{i(\gamma_{ij} w_{ij}/2)Z\otimes Z}$ and must be converted explicitly). The custom bias-preserving mixer — a general $2\times2$ unitary in NumPy — has no native gate, so it was decomposed exactly (no approximation) as
$$e^{-i\beta_i H_B(c_i)} = R_n(2\beta_i) = R_y(\theta_i) \cdot R_z(2\beta_i) \cdot R_y(-\theta_i), \qquad \theta_i = \operatorname{atan2}\!\big(-2\sqrt{c_i(1-c_i)},\, 2c_i-1\big),$$
applied per qubit with **that qubit's own** $\beta_i$, verified numerically against the original matrix (random $c_i,\beta$, matching to $10^{-8}$) before being written into the circuit; as a matrix product, $R_y(-\theta_i)$ is applied *first* in circuit order and $R_y(\theta_i)$ *last*.

**Results ($p=1$):**

| Execution | Cut value | Ratio $r$ |
|---|---|---|
| MA-QAOA idealized (NumPy statevector) | 35.139 | 0.987 |
| MA-QAOA on Nexus (Selene emulator, 5000 shots) | 35.130 | 0.987 |

The two agree to within shot noise, confirming the Guppy circuit is a faithful re-expression of the NumPy one. Because Nexus execute-jobs require a closed (parameterless) circuit, $\vec{\gamma}^*,\vec{\beta}^*$ are still optimized against the idealized NumPy simulator and baked into the Guppy circuit as compile-time constants rather than optimized in a closed loop against real Nexus shots.

### 4.5 Optimization Strategy

- **Initialization**: for the first half of the 10 runs, random uniform initialization ($\gamma_{ij} \in [0.1, \pi]$, $\beta_i \in [0.1, \pi/2]$); for the second half, warmstart by repeating the previous depth $p{-}1$'s optimal layer as the new layer, plus Gaussian perturbation, when a previous-depth result is available.
- **Refinement**: L-BFGS-B (`maxiter=300`, `ftol=1e-10`) on the full $p(m+n)$-dimensional parameter vector — no analytic gradient, so SciPy estimates it by finite differences at every iteration.
- **Runs**: 10 independent random-restart runs per $p$, reporting mean ± std and the best-of-10 result.

---

## 5. Results

### 5.1 Benchmark Comparison

| Method | Cut Value | Approx. Ratio $r$ | Std |
|--------|-----------|-------------------|-----|
| Brute Force (optimal) | 35.60 | 1.000 | — |
| Goemans-Williamson (best of 200 rounds) | 35.60 | 1.000 | mean $r=0.982$, cut $34.96 \pm 0.56$ |
| Greedy | 35.40 | 0.994 | — |
| MA-QAOA $p=1$ (best of 10 runs) | 35.14 | 0.987 | mean $r = 0.905 \pm 0.065$ |
| MA-QAOA $p=1$ **on Quantinuum Nexus** (Selene, 5000 shots) | 35.13 | 0.987 | shot noise only |
| MA-QAOA $p=2$ (best of 10 runs) | 35.51 | 0.997 | mean $r = 0.979 \pm 0.022$ |
| MA-QAOA $p=3$ (best of 10 runs) | 35.59 | 1.000 | mean $r = 0.996 \pm 0.003$ |

*Exact values populated from `quantum_grid_intelligence.py` (NumPy rows) and `run_on_nexus.py` (Nexus row). See `results/benchmark_table.csv`.*

### 5.2 Approximation Ratio vs p

Plot: `results/approximation_ratio_vs_p.png`

Shows monotonic improvement with increasing $p$, with error bars from 7 independent runs. GW and Greedy baselines shown as horizontal reference lines.

### 5.3 Fault-Zone Visualization

Plot: `results/grid_before_after.png`

Side-by-side comparison of unpartitioned grid (full cascading risk) vs. optimal partitioning (isolated fault zones).

### 5.4 Cost Landscape (MA-QAOA slice)

Plot: `results/convergence_landscape.png`

MA-QAOA's $p=1$ landscape has $m+n=17$ dimensions — too many to plot directly. We fix 15 of the 17 parameters at their found-optimal values and sweep the remaining two, chosen as the pair with the largest central-difference gradient magnitude at the optimum (i.e. the two directions the landscape is locally most sensitive to, not an arbitrary choice of axes). This directly illustrates the "optimizer sensitivity" limitation in §6.6: the slice found is comparatively smooth and monotonic near the optimum along these two axes, with the optimum sitting at a search-space boundary for at least one of them — consistent with L-BFGS-B settling into a boundary-constrained local solution rather than an interior one.

---

## 6. Honest Limitations

This section is required and central to our submission.

1. **Best-of-10 MA-QAOA ($r=0.987$ at $p=1$) is not directly comparable to the textbook QAOA vs. GW comparison.** The Farhi et al. bound ($r \ge 0.6924$ for $p=1$) and the "QAOA does not outperform GW" folklore both refer to the standard *two-angle* QAOA ansatz. MA-QAOA is a strictly more expressive ansatz (§6.2), so beating that particular bound is expected, not a violation of it — GW's own guarantee ($r \ge 0.878$) remains a fair classical baseline, and on this instance GW still reaches the exact optimum ($r=1.000$) with a mean of $r=0.982$ across rounding rounds.

2. **More classical parameters than the problem needs, at this scale.** MA-QAOA's $p=1$ circuit has $m+n=17$ free parameters (9 per-edge $\gamma$ + 8 per-qubit $\beta$) optimized classically against a search space of only $2^8=256$ states — at $p=3$ that grows to 51 parameters. With that much variational freedom relative to the problem size, part of the reported ratio plausibly reflects the classical optimizer's ability to fit an expressive parameterization to a small, fully-observable cost landscape, rather than a genuinely quantum effect. We would expect this advantage to compress as the grid scales and the parameter-to-state-space ratio drops — a claim this submission does not yet test empirically.

3. **No quantum advantage at this scale.** With 8 nodes ($2^8 = 256$ states), brute force solves the problem in microseconds. The value of this work is demonstrating the algorithm, not claiming computational superiority.

4. **Selene emulator ≠ physical quantum hardware.** We validated the MA-QAOA circuit with real shot-based execution on Quantinuum Nexus (§4.4), but against Selene's default noiseless statevector backend, not a physical device or a noisy hardware emulator. Real quantum hardware would introduce gate errors, decoherence, and measurement noise that would degrade QAOA performance; we did not exercise Nexus's noise models (`QSystemErrorModel`, `DepolarizingErrorModel`) or implement noise mitigation (ZNE, Pauli twirling) in this submission.

5. **Simplified grid topology.** The real ICE transmission network has hundreds of nodes. Our 8-node model captures geographic and topological structure but not the full complexity of the actual grid.

6. **Optimizer sensitivity.** QAOA cost landscapes are non-convex with many local minima, and MA-QAOA's larger parameter count makes this worse, not better, at higher $p$ — most $p=2$/$p=3$ runs in our benchmark did not formally converge within `maxiter=300`. While our warmstart strategy and multi-run approach mitigate this, we cannot guarantee global optimality of the variational parameters.

7. **Max-Cut is a simplification.** Real fault-zone partitioning involves additional constraints (load balancing, generation capacity within each zone, protection relay coordination) that are not captured by the pure Max-Cut formulation.

---

## 7. Conclusion

We demonstrated Multi-Angle Warm-Started QAOA (MA-QAOA) for fault-zone partitioning of Costa Rica's ICE transmission network, achieving approximation ratios well above 0.6 (the competition target) at $p=1$ and improving with depth. Goemans-Williamson remains the fairer classical baseline at this scale — it reaches the exact optimum on this instance — and MA-QAOA's high ratio should be read alongside §6's honesty about its 17–51 free classical parameters relative to a 256-state search space, not as a claim of quantum superiority. Beyond simulation, we re-expressed the optimized circuit in Guppy — with its full per-edge/per-qubit parameterization — and executed it on Quantinuum Nexus's Selene emulator, reproducing the idealized ratio (0.987 vs. 0.987) with real shot-based execution — moving this submission from "circuit constructed but never run" to a validated result on Quantinuum's own execution infrastructure. This work establishes a reproducible framework for quantum-enhanced grid optimization that could become competitive as quantum hardware scales, noise mitigation matures, and classical optimization of $\vec{\gamma},\vec{\beta}$ is replaced by a closed loop against real Nexus execution.

---

## References

1. Farhi, E., Goldstone, J., & Gutmann, S. (2014). A Quantum Approximate Optimization Algorithm. *arXiv:1411.4028*.
2. Goemans, M. X., & Williamson, D. P. (1995). Improved approximation algorithms for maximum cut and satisfiability problems using semidefinite programming. *JACM*, 42(6), 1115–1145.
3. Blekos, K., et al. (2024). A review on Quantum Approximate Optimization Algorithm and its variants.
4. Jin, J., et al. (2025). *arXiv:2504.21172*.
5. ICE Open Data Portal. https://datos-ice-se.opendata.arcgis.com
6. Quantinuum Guppy documentation. https://docs.quantinuum.com/guppy/
7. Quantinuum Nexus documentation. https://docs.quantinuum.com/nexus/
