"""Baseline selection demos, not empirical performance benchmarks.

No search-to-convergence, GPU-time, or speedup measurements are performed by
this module. It must not be used to claim BHS outperforms random search.
"""

import random
from typing import Any, Dict, List, Optional

from bhs.provenance.tags import DataProvenanceType, ProvenanceValue


class RandomSearchBaseline:
    """Sample candidates uniformly; do not invent measured computational costs."""

    def __init__(self, candidates: List[str], seed: Optional[int] = None):
        if not candidates or not all(isinstance(c, str) and c for c in candidates):
            raise ValueError("Provide a nonempty list of candidate names.")
        self.candidates = list(candidates)
        self._rng = random.Random(seed)

    def run_step(self) -> Dict[str, Any]:
        """Perform a policy-selection demo only, not a benchmark experiment."""
        chosen = self._rng.choice(self.candidates)
        probability = 1.0 / len(self.candidates)
        return {
            "selected_candidate": chosen,
            "probability": ProvenanceValue(
                value=probability,
                provenance=DataProvenanceType.DERIVED,
                source_description="Uniform random policy selection (algorithm demo)",
            ),
            "gpu_hours_used": None,
            "status": "SELECTION_DEMO_ONLY",
            "performance_measured": False,
        }


class BenchmarkRunner:
    """Placeholder awaiting an instrumented, comparable experiment protocol."""

    def __init__(self, targets: List[str]):
        if not targets or not all(isinstance(t, str) and t for t in targets):
            raise ValueError("Provide a nonempty list of target systems.")
        self.targets = list(targets)

    def evaluate_system(self, target_formula: str) -> Dict[str, Any]:
        if target_formula not in self.targets:
            raise ValueError(f"Unknown target system: {target_formula}")
        raise NotImplementedError(
            "Empirical baseline comparisons are not implemented. No convergence "
            "steps, GPU-hours, or BHS speedups have been measured. "
            "A valid comparison requires a shared search space, success criterion, "
            "cost budget, random seeds, hardware metadata, and raw run logs."
        )
