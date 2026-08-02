# bhs/search/bayesian_engine.py

import math
from typing import Dict, Any, List
from bhs.provenance.tags import ProvenanceValue, DataProvenanceType

class BayesianHypothesisSearchEngine:
    """
    Core BHS Engine independent of Streamlit UI.
    Computes exact Bayes updates and tracks data provenance for all metrics.
    """
    def __init__(self, initial_priors: Dict[str, float] = None):
        self.priors = initial_priors or {
            "H1_Olivine_Pnma": 0.50,
            "H2_Spinel_Fd3m": 0.30,
            "H3_NASICON_R3c": 0.20
        }
        # Dinamik olarak gelen priors key'lerine göre MCTS düğümlerini başlatıyoruz:
        self.mcts_nodes = {
            h_id: {"P": p_val, "Q": 0.50, "N": 1}
            for h_id, p_val in self.priors.items()
        }
        self.history: List[Dict[str, Any]] = []

    def compute_uct(self, node_id: str, c_puct: float = 1.414) -> ProvenanceValue:
        """Calculates Upper Confidence Bound for Trees (PUCT)."""
        node = self.mcts_nodes[node_id]
        total_visits = sum(n["N"] for n in self.mcts_nodes.values())
        
        exploration = c_puct * node["P"] * (math.sqrt(total_visits) / (1 + node["N"]))
        uct_val = round(node["Q"] + exploration, 3)

        return ProvenanceValue(
            value=uct_val,
            provenance=DataProvenanceType.DERIVED,
            source_description="UCT Formula: Q + c_puct * P * sqrt(N_parent) / (1 + N_node)"
        )

    def accumulate_evidence(
        self, 
        step_name: str, 
        likelihoods: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Naive Bayesian evidence update step with provenance tracking.
        """
        unnormalized = {
            h_id: self.priors[h_id] * likelihoods.get(h_id, 1.0)
            for h_id in self.priors
        }
        total_evidence_prob = sum(unnormalized.values()) or 1.0
        
        posteriors = {
            h_id: round(unnorm / total_evidence_prob, 4)
            for h_id, unnorm in unnormalized.items()
        }

        self.priors = posteriors.copy()
        for h_id in posteriors:
            self.mcts_nodes[h_id]["P"] = posteriors[h_id]

        winning_h = max(posteriors, key=posteriors.get)
        allocated_gpu_hours = round(8.0 * posteriors[winning_h] + 0.5, 2)

        record = {
            "step_name": step_name,
            "posteriors": {
                h: ProvenanceValue(p, DataProvenanceType.DERIVED, f"Sequential Bayes Update via {step_name}")
                for h, p in posteriors.items()
            },
            "winning_hypothesis": winning_h,
            "allocated_budget": ProvenanceValue(
                f"{allocated_gpu_hours} GPU-hours",
                DataProvenanceType.DERIVED,
                "Dynamic Budget Function: Base * (1 + gamma * P)"
            )
        }
        self.history.append(record)
        return record