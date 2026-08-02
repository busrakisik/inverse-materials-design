# tests/test_reconstruction_run.py

import os
import shutil
from bhs.cli import run_pipeline

def test_full_reconstruction_run():
    config_path = "configs/reconstruction_lifepo4.yaml"
    out_dir = "runs/test_run_bundle"
    
    run_pipeline(config_path, out_dir)
    
    assert os.path.exists(os.path.join(out_dir, "provenance_manifest.json"))
    assert os.path.exists(os.path.join(out_dir, "input_config.json"))
    assert os.path.exists(os.path.join(out_dir, "execution_history.json"))
    
    print("\n✅ Full Single-Command Reconstruction Integration Test Passed!")

if __name__ == "__main__":
    test_full_reconstruction_run()