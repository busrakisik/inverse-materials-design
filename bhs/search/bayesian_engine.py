"""Validated Bayesian belief updates for the BHS research prototype.

Inputs are user-supplied probabilities, NOT calibrated physical evidence.
This module performs mathematical probability updates only. It does not
perform MCTS rollouts, allocate real GPU-hours, or validate materials.
"""

import math
from typing import Any, Dict, List, Optional

from bhs.provenance.tags import DataProvenanceType, ProvenanceValue


DEFAULT_ILLUSTRATIVE_PRIORS = {
    "H1_Olivine_Pnma": 0.50,
    "H2_Spinel_Fd3m": 0.30,
    "H3_NASICON_R3c": 0.20,
}


def _validate_priors(priors: Dict[str, float]) -> Dict[str, float]:
    if not isinstance(priors, dict) or not priors:
        raise ValueError("Priors must be a nonempty hypothesis-to-probability mapping.")
    checked = {}
    for name, probability in priors.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Every hypothesis must have a nonempty string identifier.")
        if (
            isinstance(probability, bool)
            or not isinstance(probability, (int, float))
            or not math.isfinite(probability)
            or not 0.0 <= probability <= 1.0
        ):
            raise ValueError(f"Prior for {name!r} must be finite and in [0, 1].")
        checked[name] = float(probability)
    if not math.isclose(math.fsum(checked.values()), 1.0, rel_tol=0, abs_tol=1e-9):
        raise ValueError("Prior probabilities must sum to 1.0.")
    return checked


def _validate_likelihoods(likelihoods: Dict[str, float], prior_keys) -> Dict[str, float]:
    if not isinstance(likelihoods, dict) or set(likelihoods) != set(prior_keys):
        raise ValueError("Likelihoods must contain exactly the known hypothesis IDs.")
    checked = {}
    for name, probability in likelihoods.items():
        if (
            isinstance(probability, bool)
            or not isinstance(probability, (int, float))
            or not math.isfinite(probability)
            or not 0.0 <= probability <= 1.0
        ):
            raise ValueError(f"Likelihood for {name!r} must be finite and in [0, 1].")
        checked[name] = float(probability)
    return checked


class BayesianHypothesisSearchEngine:
    """Update discrete hypothesis beliefs; does not claim physical validation."""

    def __init__(self, initial_priors: Optional[Dict[str, float]] = None):
        starting = (
            dict(DEFAULT_ILLUSTRATIVE_PRIORS)
            if initial_priors is None
            else initial_priors
        )
        self.priors = _validate_priors(starting)
        # No fictional MCTS visit counts or action-value estimates are inserted.
        self.mcts_nodes = {
            name: {"P": value, "Q": None, "N": 0}
            for name, value in self.priors.items()
        }
        self.history: List[Dict[str, Any]] = []

    def compute_uct(self, node_id: str, c_puct: float = 1.414) -> ProvenanceValue:
        """Prevent displaying a fake tree-search score before rollouts exist."""
        if node_id not in self.mcts_nodes:
            raise KeyError(f"Unknown hypothesis: {node_id}")
        raise NotImplementedError(
            "PUCT/MCTS scoring is not implemented: no evaluated action values, "
            "visit counts, or real rollouts have been recorded."
        )

    def accumulate_evidence(
        self, step_name: str, likelihoods: Dict[str, float]
    ) -> Dict[str, Any]:
        """Apply Bayes' rule with stable normalization and strict validation.

        Likelihoods must be explicitly supplied for every hypothesis and are
        NOT independently verified by this function. Uses a log-sum-exp style
        normalization so tiny positive likelihoods are not lost by underflow.
        """
        if not isinstance(step_name, str) or not step_name.strip():
            raise ValueError("Evidence step_name must be nonempty.")
        valid = _validate_likelihoods(likelihoods, self.priors)

        log_weights = {
