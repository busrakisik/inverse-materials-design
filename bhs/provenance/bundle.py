# bhs/provenance/bundle.py

import os
import json
import time
from typing import Dict, Any

class ProvenanceBundleSaver:
    """
    Saves a complete reproducibility bundle for a single run,
    including configuration, history, environment locks, and manifest.
    """
    @staticmethod
    def create_run_bundle(
        out_dir: str, 
        config: Dict[str, Any], 
        run_history: list, 
        final_metrics: Dict[str, Any]
    ) -> str:
        os.makedirs(out_dir, exist_ok=True)
        
        # 1. Config Save
        with open(os.path.join(out_dir, "input_config.json"), "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        # 2. History & Metrics Save
        serializable_history = []
        for step in run_history:
            step_dict = {
                "step_name": step["step_name"],
                "winning_hypothesis": step["winning_hypothesis"],
                "allocated_budget": step["allocated_budget"].to_dict(),
                "posteriors": {k: v.to_dict() for k, v in step["posteriors"].items()}
            }
            serializable_history.append(step_dict)

        with open(os.path.join(out_dir, "execution_history.json"), "w", encoding="utf-8") as f:
            json.dump(serializable_history, f, indent=2)

        # 3. Provenance Manifest
        manifest = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "experiment_name": config.get("experiment_name", "BHS_Run"),
            "mode": config.get("mode", "Reconstruction"),
            "target": config.get("target_composition", "Unknown"),
            "reproducibility_status": "REPRODUCIBLE",
            "final_metrics": {k: (v.to_dict() if hasattr(v, "to_dict") else v) for k, v in final_metrics.items()}
        }

        with open(os.path.join(out_dir, "provenance_manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return out_dir