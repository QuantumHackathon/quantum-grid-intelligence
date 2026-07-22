# Quantum Grid Intelligence — Powering the AI Era

> Optimizing tomorrow's energy grid today.  
> Reducing Energy Losses · Improving Grid Resilience · Enabling Smarter Energy Distribution

**Quantathon CR 2026 · Challenge 1**: Sustainable, Resilient, and Green Power Grid (Fault-Zone Partitioning)

---

## The Problem

AI is driving an unprecedented surge in electricity demand:
- AI data center electricity consumption is projected to **more than double by 2030**
- Data centers could account for up to **9% of U.S. electricity demand** by 2030
- Building new transmission infrastructure takes **5–10 years**

The challenge isn't generating more electricity. **It's using today's grid more intelligently.**

## Our Approach

We model Costa Rica's ICE (Instituto Costarricense de Electricidad) transmission network as a weighted graph and solve the **fault-zone partitioning** problem — dividing the grid into isolated segments that can self-heal during faults — as a **Max-Cut** optimization problem.

### Pipeline

```
Power Grid Data → Weighted Graph → QUBO Formulation → QAOA Optimization → Optimal Partition
                                                     ↕
                                              Classical Baselines
                                          (GW, Greedy, Brute Force)
```

### Methods

| Method | Type | Approximation Guarantee |
|---|---|---|
| Brute Force | Exact (exponential) | r = 1.000 |
| Goemans-Williamson | Classical SDP relaxation | r = 1.000 |
| Greedy | Classical heuristic | r = 1.000 |
| **MA-QAOA p=1** | **Multi-Angle Warm-Started Quantum Hybrid** | **r ≈ 0.989 (Elevates 0.6924 base)** |

## SDG Alignment

- **SDG 7** (Affordable & Clean Energy): Improves grid reliability, maximizes renewable integration
- **SDG 9** (Industry, Innovation & Infrastructure): Quantum-enhanced grid optimization
- **SDG 13** (Climate Action): Reduces cascading outages, cuts diesel backup emissions

## Grid Topology

8-node representation of the ICE transmission network:

| Node | Name | Type | Capacity (MW) |
|---|---|---|---|
| 0 | Arenal | Hydroelectric | 157 |
| 1 | Miravalles | Geothermal | 163 |
| 2 | Cañas | Substation | — |
| 3 | Garabito | Thermal | 200 |
| 4 | San José | Load Center | — |
| 5 | Cachí | Hydroelectric | 103 |
| 6 | Moín | Substation | — |
| 7 | Palmar | Substation | — |

Source: Topology derived from [ICE Open Data Portal](https://datos-ice-se.opendata.arcgis.com) and public transmission maps.

## Quick Start

### Requirements

```bash
pip install -r requirements.txt
```

### Run (reproduces all figures and results)

```bash
python quantum_grid_intelligence.py
```

This generates:
- `results/approximation_ratio_vs_p.png` — Approximation ratio r vs QAOA depth p (with error bars)
- `results/grid_before_after.png` — Before/After fault-zone partitioning visualization
- `results/convergence_landscape.png` — QAOA p=1 cost landscape heatmap
- `results/grid_partitioned_qaoa.png` — Optimal partition visualization
- `results/benchmark_table.csv` — Full benchmark comparison

## Project Structure

```
quantum-grid-intelligence/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── quantum_grid_intelligence.py       # Single entry-point script (all code)
├── data/
│   └── ice_grid_topology.json         # ICE Costa Rica grid topology (8 nodes)
├── results/                           # Auto-generated outputs
│   ├── approximation_ratio_vs_p.png
│   ├── grid_before_after.png
│   ├── convergence_landscape.png
│   ├── grid_partitioned_qaoa.png
│   └── benchmark_table.csv
├── TECHNICAL_REPORT.md                # 8-page technical report
└── TOOLKIT_STATEMENT.md               # Pytket/Quantinuum SDK evaluation
```

## Algorithmic Innovation: MA-QAOA with Warm-Start

Standard QAOA struggles at low circuit depths ($p=1$), with a theoretical performance guarantee (0.6924) strictly below the classical Goemans-Williamson limit (0.878). 

To overcome this NISQ-era limitation, we implemented **Multi-Angle Warm-Started QAOA (MA-QAOA)**. Instead of a standard uniform superposition, our quantum circuit is initialized with the continuous SDP probabilities derived from Goemans-Williamson. Furthermore, rather than using two global angles, the circuit is heavily parameterized with independent angles for every node ($\beta_i$) and edge ($\gamma_{ij}$).

**Results on 8-node Grid:**
By injecting this classical bias and expanding the variational freedom, our MA-QAOA elevated the $p=1$ approximation ratio to an astonishing **98.9%**, almost perfectly solving the graph in a single depth step, significantly bypassing standard QAOA's theoretical floor (0.6924) while using the absolute minimum quantum depth resources.

## Honest Limitations

1. **No Quantum Advantage at 8 Nodes**: Classical algorithms (Brute Force, GW) achieve perfect 100% accuracy instantly on this toy graph. Our 98.9% MA-QAOA ratio serves as a proof of concept for a scalable hybrid methodology, not an absolute victory on this specific micro-instance.
2. **Statevector simulation ≠ real quantum hardware**: Without actual H2 emulator noise, our continuous QAOA amplitudes are idealized.
3. **Simplified topology**: The real ICE network has hundreds of nodes. Our model captures conceptual structure, not computational complexity.
4. **Optimizer sensitivity**: Even with a warm start, the heavily parameterized ($\vec{\gamma}, \vec{\beta}$) optimization landscape is non-convex and susceptible to local minima.

## References

- Farhi, E., Goldstone, J., & Gutmann, S. (2014). *A Quantum Approximate Optimization Algorithm*. arXiv:1411.4028.
- Goemans, M. X., & Williamson, D. P. (1995). *Improved approximation algorithms for maximum cut*. JACM, 42(6).
- Blekos, K., et al. (2024). *A review on QAOA*.
- Jin, J., et al. (2025). arXiv:2504.21172.
- ICE Open Data: [datos-ice-se.opendata.arcgis.com](https://datos-ice-se.opendata.arcgis.com)

## License

MIT
