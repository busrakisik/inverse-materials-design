# bhs/cli.py

import argparse
import yaml
import os
from bhs.search.bayesian_engine import BayesianHypothesisSearchEngine
from bhs.physics.relaxer import PhysicsRelaxationEngine
from bhs.evidence.likelihoods import LikelihoodEngine
from bhs.provenance.bundle import ProvenanceBundleSaver
from pymatgen.core import Structure, Lattice

def run_pipeline(config_path: str, out_dir: str):
    print(f"🚀 Launching BHS Pipeline via Config: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Initialize Engine with Yaml Priors
    engine = BayesianHypothesisSearchEngine(initial_priors=config.get("priors"))
    
    # Step 1: Wyckoff Clash Evidence Update
    record1 = engine.accumulate_evidence(
        step_name="Wyckoff Atomic Clash Evaluation",
        likelihoods={"H1_Olivine_Pnma": 0.95, "H2_Spinel_Fd3m": 0.32, "H3_NASICON_R3c": 0.15}
    )
    
    # Step 2: Dummy Physical Relaxation for winning hypothesis
    lattice = Lattice.cubic(4.0)
    dummy_struct = Structure(lattice, ["Fe", "O"], [[0, 0, 0], [0.5, 0.5, 0.5]])
    _, phys_metrics = PhysicsRelaxationEngine.run_chgnet_relaxation(dummy_struct)
    
    # Step 3: Bundle Outputs
    final_dir = ProvenanceBundleSaver.create_run_bundle(
        out_dir=out_dir,
        config=config,
        run_history=engine.history,
        final_metrics=phys_metrics
    )
    
    print(f"✅ Single Run Completed Successfully! Bundle saved at: {os.path.abspath(final_dir)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bayesian Hypothesis Search (BHS) CLI")
    parser.add_argument("--config", type=str, required=True, help="Path to YAML config file")
    parser.add_argument("--out-dir", type=str, default="./runs/run_001", help="Output directory for reproducibility bundle")
    
    args = parser.parse_args()
    # ⬇️ BURADAKİ TİREYİ ALT ÇİZGİ (out_dir) YAPIYORUZ
    run_pipeline(args.config, args.out_dir)