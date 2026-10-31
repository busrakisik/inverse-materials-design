# BEGIN OF COMPLETE BHS LEGACY ENSEMBLE VALIDATOR — CHECK THIS LINE ON GITHUB
"""Fail-closed compatibility wrapper for the old 'ensemble' MLFF interface.

Only one CHGNet validator is invoked. No MACE, M3GNet, DFT, or independent
model is executed, and no calibrated confidence score, ensemble agreement,
thermodynamic stability, or synthesis approval can be inferred from a
single model's potential energy. Test doubles are not physical validation.
"""

import math
from typing import Any, Dict

from pymatgen.core import Structure

from src.imd_pipeline.validation.mlff_validator import MLFFValidator


class MultiMLFFEnsembleValidator:
    """Expose an actual primary CHGNet result without fake ensemble metrics."""

    def __init__(self, use_gpu: bool = False):
        # No model weights are loaded by MLFFValidator.__init__.
        self.primary_validator = MLFFValidator(use_gpu=use_gpu)

    def evaluate_with_ensemble(self, structure: Structure) -> Dict[str, Any]:
        """Call only the primary MLFF validator, then declare no ensemble run.

        This legacy method name is retained for import compatibility. A
        successful primary model prediction does not authorize an ensemble
        confidence score or material-stability decision.
        """
        if not isinstance(structure, Structure) or len(structure) == 0:
            raise ValueError("A nonempty pymatgen Structure is required.")

        # Exceptions are deliberately propagated: no fallback model or
        # placeholder result may be substituted when CHGNet fails.
        primary = self.primary_validator.evaluate_and_relax(structure)
        if not isinstance(primary, dict):
            raise RuntimeError("Primary MLFF validator returned no valid result.")
        if (
            primary.get("engine") != "CHGNet"
            or primary.get("execution_status") != "CHGNET_OPTIMIZER_RETURNED_OUTPUT"
            or primary.get("model_output_provenance") != "MLFF_PREDICTION_NOT_EXPERIMENT"
        ):
            raise RuntimeError(
                "A verified primary CHGNet execution report is required. "
                "No ensemble confidence or approval can be inferred."
            )

        # The primary adapter returns predicted potential energy per atom,
        # NOT a formation energy. Do not accept missing or non-finite values.
        potential = primary.get("potential_energy_ev_per_atom")
        if isinstance(potential, bool) or not isinstance(potential, (int, float)):
            raise RuntimeError("Primary CHGNet potential energy is unavailable.")
        try:
            energy = float(potential)
        except (OverflowError, ValueError) as exc:
            raise RuntimeError("Primary CHGNet potential energy is invalid.") from exc
        if not math.isfinite(energy):
            raise RuntimeError("Primary CHGNet potential energy is nonfinite.")

        # Guard against stale/fabricated downstream results or an incompatible
        # primary implementation accidentally making unsupported claims.
        unverified_fields = (
            "e_form", "formation_energy_ev_per_atom",
            "synthesizability_score", "band_gap_class", "estimated_gap_eV",
            "ensemble_confidence", "is_ensemble_approved",
        )
        if any(primary.get(field) is not None for field in unverified_fields):
            raise RuntimeError(
                "Primary result contains unsupported scientific or ensemble "
                "claims; refuse to publish a synthetic consensus."
            )

        # Copy rather than mutate the primary model's output dictionary.
        result = dict(primary)
        result.update({
            "primary_model": "CHGNet",
            "primary_model_execution_status": "CHGNET_OPTIMIZER_RETURNED_OUTPUT",
            "secondary_models_executed": [],
            "secondary_model_execution_status": "NOT_RUN",
            "cross_model_comparison_status": "NOT_RUN",
            "model_disagreement_ev_per_atom": None,
            "ensemble_confidence": None,
            "ensemble_uncertainty_ev_per_atom": None,
            "ensemble_status": "NOT_EVALUATED",
            "is_ensemble_approved": None,
            "stability_approval_status": "NOT_EVALUATED",
            "scientific_ensemble_interpretation": (
                "NO ENSEMBLE COMPARISON PERFORMED. Only the primary CHGNet "
                "potential-energy prediction is available; no independent "
                "MACE, M3GNet, or DFT result was calculated or compared. "
                "A single predicted potential energy cannot establish "
                "confidence, thermodynamic stability, or synthesis approval."
            ),
        })
        return result

# END OF COMPLETE BHS LEGACY ENSEMBLE VALIDATOR — CHECK THIS LINE ON GITHUB
