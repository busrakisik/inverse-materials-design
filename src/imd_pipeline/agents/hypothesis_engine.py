# BEGIN OF COMPLETE BHS LEGACY HYPOTHESIS ENGINE — CHECK THIS LINE ON GITHUB
"""Safe illustrative hypothesis registry: NO physical ranking or selection.

No formation energies, hull positions, MLFF comparisons, patent results,
thermal measurements, diffusion barriers, or Pareto optimizations are computed.
This file preserves the legacy API without fabricating scientific evidence.
"""

from typing import Any, Dict, List


# Conceptual families only; NOT ranked or independently verified candidates.
ILLUSTRATIVE_FAMILIES = (
    ("HYP-A", "NASICON-like open-framework concept"),
    ("HYP-B", "Spinel / disordered-rocksalt concept"),
    ("HYP-C", "Olivine-like channel concept"),
)


class HypothesisAndExplainabilityEngine:
    """Registry for illustrative hypotheses; no autonomous discovery."""

    @staticmethod
    def evaluate_competing_hypotheses(targets: List[str]) -> Dict[str, Any]:
        """List illustrative families without evaluating or selecting any.

        `targets` are caller-supplied research objectives, NOT demonstrated
        properties. All candidate quantities remain unknown until supported
        by independently traceable calculations or measurements.
        """
        if not isinstance(targets, list) or not targets:
            raise ValueError("targets must be a nonempty list of research objectives.")
        if any(not isinstance(t, str) or not t.strip() for t in targets):
            raise ValueError("Every research target must be nonempty text.")
        checked_targets = [t.strip() for t in targets]
        if len(set(checked_targets)) != len(checked_targets):
            raise ValueError("Research targets must not be duplicated.")

        hypotheses = [
            {
                "id": identifier,
                "family": family,
                "candidate_provenance": "ILLUSTRATIVE_TEMPLATE",
                "confidence_score": None,
                "confidence_std": None,
                "pros": None,
                "cons": None,
                "chosen": False,
                "selection_reason": None,
                "physical_evidence_status": "NOT_VERIFIED",
                "comparison_status": "NOT_EVALUATED",
            }
            for identifier, family in ILLUSTRATIVE_FAMILIES
        ]
        return {
            "research_targets": checked_targets,
            "targets_provenance": "CALLER_SUPPLIED_NOT_VERIFIED",
            "competing_hypotheses": hypotheses,
            "chosen_hypothesis": None,
            "selection_status": "NOT_EVALUATED",
            "candidate_generation_status": "NOT_RUN",
            "pareto_optimization_status": "NOT_RUN",
            "selection_narrative": (
                "NO HYPOTHESIS HAS BEEN SELECTED. These are illustrative "
                "material-family concepts, not generated or evaluated crystal "
                "structures. No validated performance comparison, confidence "
                "estimate, physical calculation, or patent review exists here."
            ),
        }

    @staticmethod
    def explain_why_selected(candidate_data: Dict[str, Any]) -> List[str]:
        """Return a transparent non-selection note, not fabricated evidence.

        This function does not validate or adopt claims in candidate_data.
        It deliberately refuses to turn unverified data into a justification.
        """
        if not isinstance(candidate_data, dict):
            raise ValueError("candidate_data must be a dictionary.")
        return [
            "NOT_EVALUATED: no independently verified candidate selection.",
            "NOT_RUN: no formation-energy or convex-hull ranking calculated.",
            "NOT_RUN: no CHGNet/MACE comparison or relaxation verified.",
            "NOT_RUN: no lithium diffusion, thermal, or rate performance evaluated.",
            "NOT_CHECKED: no patent prior-art or scientific novelty search performed.",
        ]

# END OF COMPLETE BHS LEGACY HYPOTHESIS ENGINE — CHECK THIS LINE ON GITHUB
