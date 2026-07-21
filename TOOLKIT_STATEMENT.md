## Software Toolkit Statement — Pytket & Quantinuum Ecosystem

We implemented QAOA using a pure NumPy/SciPy statevector simulation for rapid prototyping and exact reproducibility, with a parallel Pytket circuit builder for Quantinuum H2 emulator submission.

**What worked:** The statevector approach provided exact, noiseless QAOA simulation for 8 qubits without external quantum SDK dependencies, ensuring full reproducibility. SciPy's L-BFGS-B optimizer with warmstarting from grid search proved effective for parameter optimization. NetworkX for graph construction and CVXPY for SDP-based Goemans-Williamson baseline were straightforward and reliable.

**What did not:** The QAOA cost landscape is highly non-convex for p>1, causing significant optimizer variance across random initializations. Warmstarting from p-1 parameters helped but did not eliminate the issue. The gradient-based L-BFGS-B optimizer frequently converges to local minima in higher-p parameter spaces.

**What was missing:** We did not have access to the Quantinuum H2 emulator API during development, so all results are from statevector simulation. The Pytket circuit was constructed but not executed on hardware. Noise-aware simulation (shot-based sampling, realistic gate errors) was not implemented due to time constraints. A production version would benefit from Pytket's native noise models and the H2 emulator's exact statevector capabilities for validation.
