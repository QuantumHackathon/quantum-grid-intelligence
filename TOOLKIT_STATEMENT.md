We implemented MA-QAOA for Max-Cut using a vectorized NumPy statevector simulation for rapid classical optimization, and re-expressed the optimized circuit in Guppy for execution on Quantinuum Nexus (Selene emulator).

**What worked:**
NumPy vectorization drastically reduced simulation time (from ~17m to ~76s), making our 17-to-51 parameter optimization feasible. SciPy’s L-BFGS-B, NetworkX, and CVXPY (for Goemans-Williamson) were highly reliable. Guppy successfully compiled our per-edge/per-qubit circuit, and executing on Nexus perfectly matched our idealized statevector ($r=0.987$ vs $0.987$).

**What did not:**
- *Convergence:* Without analytic gradients, L-BFGS-B struggled with high parameter counts at higher depths ($p \ge 2$).
- *Guppy conventions:* `zz_phase` and matrix-product ordering silently differ from standard physics conventions, requiring careful translation.
- *Loop unrolling:* Guppy rejected nested Python loops (`for ... in py()`); we bypassed this by flattening all gates into a single list before compilation.

**What was missing:**
Our Nexus execution used the noiseless Selene backend. We did not test noise models or submit to physical hardware. Furthermore, our classical optimization loop runs against the local simulator rather than against real Nexus shots.
