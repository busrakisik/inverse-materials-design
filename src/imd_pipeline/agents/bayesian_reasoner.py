
"""Compatibility adapter for the audited BHS Bayesian probability engine.

This module performs *only* mathematical Bayesian updates. It does not run
MCTS/PUCT rollouts, evaluate materials, allocate GPU hours, or calibrate
likelihoods. Legacy default priors and caller-supplied likelihoods are
ILLUSTRATIVE/NOT_VERIFIED until independently justified.

The legacy Streamlit interface must be rewritten before its MCTS and budget
panels can present these safe outputs. This adapter intentionally refuses
to invent missing scientific results.
"""

from typing import Any, Dict, Optional

from bhs.search.bayesian_engine import (
    BayesianHypothesisSearchEngine as AuditedBayesianEngine,
)


ILLUSTRATIVE_LEGACY_PRIORS = {
    "H1_NASICON": 0.41,
    "H2_Spinel": 0.33,
    "H3_Olivine": 0.26,
}


class BayesianHypothesisSearchEngine:
    """Legacy method names backed by the audited Bayesian-update engine."""

    def __init__(self, initial_priors: Optional[Dict[str, float]] = None):
        supplied_priors = (
            dict(ILLUSTRATIVE_LEGACY_PRIORS)
            if initial_priors is None
            else initial_priors
        )
        self._engine = AuditedBayesianEngine(initial_priors=supplied_priors)
        self.priors = self._engine.priors
        self.mcts_nodes = self._engine.mcts_nodes
        self.history = []
        self.prior_provenance = (
            "ILLUSTRATIVE_DEFAULTS"
            if initial_priors is None
            else "CALLER_SUPPLIED_NOT_VERIFIED"
        )

    def compute_uct(self, node_id: str, c_puct: float = 1.414):
        """Fail closed: PUCT scores require real evaluated rewards/visits."""
        return self._engine.compute_uct(node_id, c_puct=c_puct)

    def accumulate_sequential_evidence(
        self, step_name: str, likelihoods: Dict[str, float]
    ) -> Dict[str, Any]:
        """Apply validated Bayes math; report no fictional search or GPU work.

        The audited engine validates exact hypothesis keys, finite likelihood
        values in [0, 1], and nonzero evidence normalization. On failure it
        does not mutate state. Evidence calibration is NOT_VERIFIED.
        """
        previous_priors = dict(self._engine.priors)
        audited_record = self._engine.accumulate_evidence(
            step_name=step_name,
            likelihoods=likelihoods,
        )
        posteriors = {
            name: float(posterior.value)
            for name, posterior in audited_record["posteriors"].items()
        }
        self.priors = self._engine.priors

        # Preserve a useful, explicitly unverified legacy history schema.
        step_record = {
            "step_name": step_name,
            "prev_priors": previous_priors,
            "likelihoods": dict(likelihoods),
            "posteriors": dict(posteriors),
            "evidence_verification_status": "NOT_VERIFIED",
            "mcts_status": "NOT_RUN",
            "budget_status": "NOT_ALLOCATED",
        }
        self.history.append(step_record)

        return {
            "step_name": step_name,
            "prev_priors": previous_priors,
            "likelihoods_applied": dict(likelihoods),
            "updated_posteriors": posteriors,
            "winning_hypothesis": audited_record["winning_hypothesis"],
            "allocated_budget": None,
            "budget_status": "NOT_ALLOCATED",
            "uct_scores": {name: None for name in posteriors},
            "mcts_status": "NOT_RUN",
            "evidence_verification_status": "NOT_VERIFIED",
            "prior_provenance": self.prior_provenance,
            "scientific_interpretation": (
                "Illustrative mathematical Bayesian update from uncalibrated "
                "caller-supplied likelihoods. No MCTS visits, rewards, "
                "GPU allocation, physical calculation, or materials validation."
            ),
        }

