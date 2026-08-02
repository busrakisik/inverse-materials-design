# src/imd_pipeline/agents/bayesian_reasoner.py

import math
from typing import Dict, Any, List

class BayesianHypothesisSearchEngine:
    """
    Mathematical Core for Bayesian Hypothesis Search (BHS) and Adaptive MCTS.
    Calculates exact P(H_i | E_1:k) via Sequential Evidence Likelihood Decomposition
    and Upper Confidence Bound for Trees (UCT).
    """
    def __init__(self):
        # Initial Prior Distribution P(H)
        self.priors = {
            "H1_NASICON": 0.41,
            "H2_Spinel": 0.33,
            "H3_Olivine": 0.26
        }
        # MCTS Node Statistics: {Node: {"P": Prior, "Q": Reward, "N": Visits}}
        self.mcts_nodes = {
            "H1_NASICON": {"P": 0.41, "Q": 0.88, "N": 31},
            "H2_Spinel":  {"P": 0.33, "Q": 0.54, "N": 9},
            "H3_Olivine": {"P": 0.26, "Q": 0.42, "N": 5}
        }
        self.history = []

    def compute_uct(self, node_id: str, c_puct: float = 1.414) -> float:
        """Calculates Upper Confidence Bound applied to Trees (UCT)."""
        node = self.mcts_nodes[node_id]
        total_visits = sum(n["N"] for n in self.mcts_nodes.values())
        
        # UCT = Q + c * P * sqrt(N_parent) / (1 + N_node)
        exploration = c_puct * node["P"] * (math.sqrt(total_visits) / (1 + node["N"]))
        uct_val = node["Q"] + exploration
        return round(uct_val, 3)

    def accumulate_sequential_evidence(
        self, 
        step_name: str, 
        likelihoods: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calculates exact Bayes Update:
        P(H_i | E_k) = P(E_k | H_i) * P(H_i | E_{k-1}) / SUM(P(E_k | H_j) * P(H_j))
        """
        unnormalized = {}
        for h_id, current_prob in self.priors.items():
            l_k = likelihoods.get(h_id, 1.0)
            unnormalized[h_id] = current_prob * l_k

        total_evidence_prob = sum(unnormalized.values())
        
        posteriors = {}
        for h_id, unnorm in unnormalized.items():
            posteriors[h_id] = round(unnorm / total_evidence_prob, 4)

        prev_priors = self.priors.copy()
        self.priors = posteriors  # Dynamic Bayes state update

        # Update MCTS priors with new posteriors
        for h_id in posteriors:
            self.mcts_nodes[h_id]["P"] = posteriors[h_id]

        record = {
            "step_name": step_name,
            "likelihoods": likelihoods,
            "prev_priors": prev_priors,
            "posteriors": posteriors
        }
        self.history.append(record)

        winning_h = max(posteriors, key=posteriors.get)
        
        # Dynamic Budget Allocation: Budget = f(P(H), Uncertainty)
        allocated_gpu_hours = round(8.0 * posteriors[winning_h] + 0.5, 2)

        return {
            "step_name": step_name,
            "prev_priors": prev_priors,
            "likelihoods_applied": likelihoods,
            "updated_posteriors": posteriors,
            "winning_hypothesis": winning_h,
            "allocated_budget": f"{allocated_gpu_hours} GPU-hours",
            "uct_scores": {h: self.compute_uct(h) for h in posteriors}
        }