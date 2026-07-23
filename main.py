import subprocess
import sys
import os

def main():
    print("=" * 60)
    print("Quantum Grid Intelligence: MA-QAOA Fault-Zone Partitioning")
    print("=" * 60)
    
    # 1. Run local baseline and idealized simulations
    print("\n[1/2] Running local MA-QAOA simulation & classical baselines...")
    print("This will generate graphs and run parameter optimization (may take ~1-2 minutes).")
    try:
        subprocess.run([sys.executable, "quantum_grid_intelligence.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running quantum_grid_intelligence.py: {e}")
        sys.exit(1)
        
    # 2. Run Guppy/Nexus execution
    print("\n[2/2] Running Guppy/Nexus execution on Selene emulator...")
    print("Note: Requires active qnx.login().")
    # Activating virtual environment python if available, otherwise just use current sys.executable
    python_exec = sys.executable
    if os.path.exists(".venv/bin/python"):
        python_exec = ".venv/bin/python"
    
    try:
        subprocess.run([python_exec, "run_on_nexus.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running run_on_nexus.py: {e}")
        sys.exit(1)
        
    print("\n" + "=" * 60)
    print("Pipeline Complete! All benchmarks and plots reproduced.")
    print("Results saved in the 'results/' directory.")
    print("=" * 60)

if __name__ == "__main__":
    main()
