"""
Render all Quantum Grid Intelligence diagrams to docs/diagrams/output/{horizontal,vertical}/ (SVG + PNG).
Usage: python scripts/diagrams/render-all.py   (from repo root)
Requires: pip install graphviz, and the Graphviz `dot`/`neato` binaries on PATH.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent

scripts = [
    "01-pipeline-overview.py",
    "02-maqaoa-circuit.py",
    "03-benchmark-tree.py",
    "04-guppy-nexus-execution.py",
    "05-grid-topology-schematic.py",
]

base   = Path(__file__).parent
errors = []

print(f"Rendering {len(scripts)} diagrams (horizontal + vertical) → docs/diagrams/output/\n")
for script in scripts:
    path   = base / script
    result = subprocess.run(
        [sys.executable, str(path)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"✗ {script}\n{result.stderr}")
        errors.append(script)
    elif result.stdout:
        print(result.stdout.strip())

if errors:
    print(f"\n{len(errors)} script(s) failed: {errors}")
    sys.exit(1)
else:
    print(f"\nAll {len(scripts)} diagrams rendered successfully (x2 orientations each).")
