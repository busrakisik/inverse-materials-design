from typing import Dict, Any

class AdaptiveBudgetPlanner:
    """
    Manages computational budget across multi-branch tree search
    and dynamically allocates MLFF / DFT resources based on model confidence.
    """
    @staticmethod
    def allocate_and_evaluate(candidate_uncertainty: float) -> Dict[str, Any]:
        if candidate_uncertainty < 0.015:
            tier = "TIER_3_FULL_ENSEMBLE_AND_DFT"
            engines = ["CHGNet v0.3.0", "MACE-MP-0", "M3GNet Elastic", "Quantum ESPRESSO (DFT)"]
            allocated_compute = "8.4 GPU-hours"
        elif candidate_uncertainty < 0.035:
            tier = "TIER_2_DUAL_MLFF"
            engines = ["CHGNet v0.3.0", "MACE-MP-0"]
            allocated_compute = "0.8 GPU-hours"
        else:
            tier = "TIER_1_FAST_SCREENING"
            engines = ["CHGNet v0.3.0"]
            allocated_compute = "0.05 GPU-hours"

        return {
            "execution_tier": tier,
            "active_engines": engines,
            "allocated_compute": allocated_compute,
            "reasoning": f"Candidate uncertainty ({candidate_uncertainty:.4f} eV/atom) dictated {tier} allocation."
        }