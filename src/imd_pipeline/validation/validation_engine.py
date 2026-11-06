
"""Safe legacy validation interface; no synthetic relaxation or formation energy.

Geometric pair distances use pymatgen and may flag sites for inspection, but
an arbitrary distance cutoff does not establish chemical bonding, physical
stability, or synthesizability. CHGNet is optional and is run only when
explicitly requested. Its potential energy is NOT a formation energy or
a thermodynamic stability result. This interface never fabricates physics.
"""

import math
from typing import Any, Dict, List, Optional

from pymatgen.core import Structure

from src.imd_pipeline.validation.mlff_validator import MLFFValidator


class ValidationFinding:
    """Legacy result interface; a finding is not a scientific certification."""

    def __init__(
        self, validator: str, severity: str, message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.validator = validator
        self.severity = severity
        self.message = message
        self.details = {} if details is None else details


class ValidationEngine:
    """Heuristic geometry screening and optional explicit CHGNet evaluation."""

    GEOMETRIC_SCREENING_CUTOFF_ANGSTROM = 1.1

    def __init__(self, use_mlff: bool = True, e_form_threshold: float = 0.35):
        if not isinstance(use_mlff, bool):
            raise ValueError("use_mlff must be a boolean.")
        if isinstance(e_form_threshold, bool) or not isinstance(
            e_form_threshold, (int, float)
        ):
            raise ValueError("e_form_threshold must be a finite number.")
        try:
            threshold = float(e_form_threshold)
        except (OverflowError, ValueError) as exc:
            raise ValueError("e_form_threshold is not representable.") from exc
        if not math.isfinite(threshold):
            raise ValueError("e_form_threshold must be a finite number.")

        # The legacy threshold is retained but is NEVER used to infer stability.
        self.use_mlff = use_mlff
        self.e_form_threshold = threshold
        self._chgnet_model = None  # No model or weights loaded in __init__.
        self.mlff_validator = MLFFValidator() if use_mlff else None

    @staticmethod
    def _validate_structure(structure: Structure) -> None:
        if not isinstance(structure, Structure) or len(structure) == 0:
            raise ValueError("A nonempty pymatgen Structure is required.")

    def _geometry_finding(self, structure: Structure) -> ValidationFinding:
        """Inspect distinct-site minimum-image distances only, without physics."""
        cutoff = self.GEOMETRIC_SCREENING_CUTOFF_ANGSTROM
        minimum = None
        short_pairs = []
        for i in range(len(structure)):
            for j in range(i + 1, len(structure)):
                distance = float(structure.get_distance(i, j))
                if not math.isfinite(distance) or distance < 0.0:
                    raise ValueError("A finite nonnegative pair distance is required.")
                minimum = distance if minimum is None else min(minimum, distance)
                if distance < cutoff:
                    short_pairs.append({
                        "site_indices": [i, j],
                        "species": [
                            str(structure[i].species), str(structure[j].species)
                        ],
                        "distance_angstrom": distance,
                    })

        status = "REVIEW" if short_pairs else "NO_SHORT_PAIRS_AT_CUTOFF"
        return ValidationFinding(
            validator="GeometricDistanceScreen",
            severity="REVIEW" if short_pairs else "INFO",
            message=(
                "Heuristic short-distance screening: review flagged site pairs; "
                "not proof of atomic overlap or material instability."
                if short_pairs else
                "No distinct-site pairs below the heuristic distance cutoff; "
                "physical validity and stability remain unverified."
            ),
            details={
                "screening_status": status,
                "screening_method": "DISTINCT_SITE_PBC_DISTANCE_HEURISTIC",
                "cutoff_angstrom": cutoff,
                "minimum_pair_distance_angstrom": minimum,
                "short_pairs": short_pairs,
                "physical_stability_status": "NOT_EVALUATED",
                "structure_provenance": "CALLER_SUPPLIED_NOT_VERIFIED",
            },
        )
    def run_all(self, structure: Structure) -> List[ValidationFinding]:
        """Return explicit screening and execution status, never a stability PASS."""
        self._validate_structure(structure)
        findings = [self._geometry_finding(structure)]

        if not self.use_mlff:
            findings.append(ValidationFinding(
                validator="MLFFValidator",
                severity="NOT_RUN",
                message="CHGNet disabled; no relaxation or energy was computed.",
                details={
                    "execution_status": "NOT_RUN",
                    "potential_energy_ev_per_atom": None,
                    "e_form": None,
                    "formation_energy_status": "NOT_CALCULATED",
                    "convergence_status": "NOT_VERIFIED",
                    "forces_zeroed": None,
                    "stability_status": "NOT_EVALUATED",
                    "e_form_threshold_application": "NOT_APPLIED",
                },
            ))
            return findings
        
        try:
            output = self.mlff_validator.evaluate_and_relax(structure)
        except Exception as exc:
            findings.append(ValidationFinding(
                validator="MLFFValidator",
                severity="ERROR",
                message=(
                    "CHGNet unavailable or execution failed. No placeholder "
                    "physics result was substituted."
                ),
                details={
                    "execution_status": "FAILED",
                    "error_type": type(exc).__name__,
                    "potential_energy_ev_per_atom": None,
                    "e_form": None,
                    "formation_energy_status": "NOT_CALCULATED",
                    "convergence_status": "NOT_VERIFIED",
                    "forces_zeroed": None,
                    "stability_status": "NOT_EVALUATED",
                    "e_form_threshold_application": "NOT_APPLIED",
                },
            ))
            return findings
            
        if (
            not isinstance(output, dict)
            or output.get("engine") != "CHGNet"
            or output.get("execution_status") != "CHGNET_OPTIMIZER_RETURNED_OUTPUT"
            or output.get("model_output_provenance")
            != "MLFF_PREDICTION_NOT_EXPERIMENT"
        ):
            raise RuntimeError("Invalid CHGNet provenance; refusing physics report.")
        energy = output.get("potential_energy_ev_per_atom")
        if isinstance(energy, bool) or not isinstance(energy, (int, float)):
            raise RuntimeError("Missing CHGNet potential energy; no substitute.")
        try:
            checked_energy = float(energy)
        except (OverflowError, ValueError) as exc:
            raise RuntimeError("Invalid CHGNet potential energy.") from exc
        if not math.isfinite(checked_energy):
            raise RuntimeError("Nonfinite CHGNet potential energy.")
        if any(output.get(key) is not None for key in (
            "e_form", "formation_energy_ev_per_atom",
            "synthesizability_score", "band_gap_class", "estimated_gap_eV",
            "converged",
        )):
            raise RuntimeError("Unsupported physical claim in CHGNet result.")

        findings.append(ValidationFinding(
            validator="MLFFValidator",
            severity="INFO",
            message=(
                "CHGNet returned a model-predicted potential energy. "
                "No formation energy, stability, or convergence proof."
            ),
            details={
                "execution_status": "CHGNET_OPTIMIZER_RETURNED_OUTPUT",
                "model_output_provenance": "MLFF_PREDICTION_NOT_EXPERIMENT",
                "potential_energy_ev_per_atom": checked_energy,
                "e_form": None,
                "formation_energy_status": "NOT_CALCULATED",
                "convergence_status": "NOT_VERIFIED",
                "forces_zeroed": None,
                "stability_status": "NOT_EVALUATED",
                "e_form_threshold_application": "NOT_APPLIED",
                "relaxed_structure": output.get("relaxed_structure"),
            },
        ))
        return findings

    def _relax_and_evaluate(self, structure: Structure, min_dist: float):
        """Disabled legacy API; it formerly synthesized formation energies."""
        raise NotImplementedError(
            "Legacy formation-energy and fake relaxation API disabled. "
            "Use run_all for explicit status and optional CHGNet potential energy."
        )






