"""Safe property-assessment interface for the BHS research prototype.

No electronic-structure calculation, experimentally supported band-gap
prediction, or validated synthesis-feasibility model runs in this module.
Geometry or chemical composition alone must never be used here to invent
an electronic band gap or a probability of successful synthesis.

These names are preserved for legacy callers. Returning None denotes an
unknown property, not a numeric zero or a negative scientific finding.
"""

import math
from typing import Any, Dict, Optional

from pymatgen.core import Structure


class PropertyFilter:
    """Report unevaluated properties instead of fabricating predictions."""

    @staticmethod
    def _validate_structure(structure: Structure) -> None:
        if not isinstance(structure, Structure) or len(structure) == 0:
            raise ValueError("A nonempty pymatgen Structure is required.")

    @staticmethod
    def assess_synthesizability(structure: Structure) -> Dict[str, Any]:
        """Return an explicit non-assessment with no invented confidence score."""
        PropertyFilter._validate_structure(structure)
        return {
            "synthesizability_score": None,
            "synthesizability_status": "NOT_EVALUATED",
            "synthesis_experiment_status": "NOT_RUN",
            "calibrated_prediction_status": "NOT_AVAILABLE",
            "scientific_interpretation": (
                "NO SYNTHESIZABILITY ASSESSMENT PERFORMED. Atomic-distance "
                "uniformity, overlap heuristics, or symmetry alone do not "
                "establish whether a crystal can be synthesized. No validated "
                "synthesis model, experimental evidence, or uncertainty "
                "calibration was used."
            ),
        }

    @staticmethod
    def estimate_synthesizability(structure: Structure) -> Optional[float]:
        """Legacy API: return unknown, not a fabricated 0-to-1 score."""
        return PropertyFilter.assess_synthesizability(structure)[
            "synthesizability_score"
        ]

    @staticmethod
    def classify_band_gap(
        structure: Structure, e_form: Optional[float] = None
    ) -> Dict[str, Any]:
        """Do not classify electronic structure from composition or e_form.

        `e_form`, if supplied, is a caller-provided unverified number. It is
        not used as a surrogate for electronic band-structure calculations.
        """
        PropertyFilter._validate_structure(structure)
        if e_form is not None:
            if isinstance(e_form, bool) or not isinstance(e_form, (int, float)):
                raise ValueError("e_form must be None or a finite number.")
            try:
                checked = float(e_form)
            except (OverflowError, ValueError) as exc:
                raise ValueError("e_form cannot be represented safely.") from exc
            if not math.isfinite(checked):
                raise ValueError("e_form must be None or a finite number.")

        return {
            "band_gap_class": None,
            "estimated_gap_eV": None,
            "band_gap_status": "NOT_CALCULATED",
            "electronic_structure_method": None,
            "electronic_structure_calculation_status": "NOT_RUN",
            "band_gap_uncertainty_eV": None,
            "input_e_form_provenance": (
                "CALLER_SUPPLIED_NOT_VERIFIED"
                if e_form is not None else "NOT_PROVIDED"
            ),
            "input_e_form_used_for_gap_prediction": False,
            "scientific_interpretation": (
                "NO BAND-GAP CALCULATION PERFORMED. Element identities, "
                "stoichiometry, and a supplied formation-energy value do "
                "not determine band-gap magnitude or metallic character. "
                "An appropriate electronic-structure calculation or "
                "traceable measurement is required."
            ),
        }

