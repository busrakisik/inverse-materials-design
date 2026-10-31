# BEGIN OF COMPLETE BHS LEGACY ORCHESTRATOR — CHECK THIS LINE ON GITHUB
"""Explicit single-candidate CHGNet orchestration without fabricated discovery.

This compatibility module does NOT implement an LLM candidate generator,
Bayesian tree search, autonomous refinement, secondary models, DFT, or
experimental verification. No default LiFePO4 structure, relaxation, formation
energy, convergence, or stability result is manufactured. An actual pymatgen
candidate must be supplied explicitly to run the optional CHGNet adapter.

Passing mock-based software tests is not evidence of materials discovery.
"""

from dataclasses import dataclass, field
import math
from typing import Any, Dict, List, Optional

from pymatgen.core import Composition, Structure

from src.imd_pipeline.validation.mlff_validator import MLFFValidator


@dataclass
class DiscoveryResult:
    """Legacy-compatible record; False means *not verified*, not unstable."""

    target_formula: str
    is_stable: bool
    iterations_taken: int
    final_structure: Optional[Structure]
    history: List[Dict[str, Any]] = field(default_factory=list)
    execution_status: str = "NOT_RUN"
    stability_status: str = "NOT_EVALUATED"
    candidate_generation_status: str = "NOT_RUN"
    convergence_status: str = "NOT_VERIFIED"
    scientific_interpretation: str = (
        "No independently verified materials-stability determination was made."
    )


class Orchestrator:
    """Legacy orchestrator: at most one explicit, caller-supplied candidate.

    Even when max_iterations > 1, no autonomous generator or retries exist;
    claiming a search loop would be scientifically incorrect. A CHGNet result
    is a potential-energy prediction, never a formation-energy/stability proof.
    """

    def __init__(
        self,
        max_iterations: int = 5,
        e_form_threshold: float = 0.25,
        use_gpu: bool = False,
        use_mlff: bool = True,
    ):
        if (
            isinstance(max_iterations, bool)
            or not isinstance(max_iterations, int)
            or max_iterations < 1
        ):
            raise ValueError("max_iterations must be a positive integer.")
        if not isinstance(use_mlff, bool):
            raise ValueError("use_mlff must be a boolean.")
        if not isinstance(use_gpu, bool):
            raise ValueError("use_gpu must be a boolean.")
        if isinstance(e_form_threshold, bool) or not isinstance(
            e_form_threshold, (int, float)
        ):
            raise ValueError("e_form_threshold must be a finite number.")
        try:
            checked_threshold = float(e_form_threshold)
        except (OverflowError, ValueError) as exc:
            raise ValueError("e_form_threshold is not representable.") from exc
        if not math.isfinite(checked_threshold):
            raise ValueError("e_form_threshold must be a finite number.")

        self.max_iterations = max_iterations
        # Retained only for old callers; this value is NEVER used as a
        # formation-energy or physical-stability approval rule.
        self.e_form_threshold = checked_threshold
        self.use_gpu = use_gpu
        self.use_mlff = use_mlff
        # MLFFValidator.__init__ never downloads or runs the model.
        self.mlff_validator = MLFFValidator(use_gpu=use_gpu)

    @staticmethod
    def _parse_target_formula(target_formula: str) -> Composition:
        if not isinstance(target_formula, str) or not target_formula.strip():
            raise ValueError("target_formula must be a nonempty chemical formula.")
        if len(target_formula) > 256:
            raise ValueError("target_formula exceeds the allowed length.")
        try:
            composition = Composition(target_formula.strip())
            if not composition or composition.num_atoms <= 0:
                raise ValueError("Empty composition.")
            return composition
        except Exception as exc:
             raise ValueError("target_formula must be a valid chemical formula.") from exc

    @staticmethod
    def _validate_candidate(candidate: Structure, target: Composition) -> None:
        if not isinstance(candidate, Structure) or len(candidate) == 0:
            raise ValueError("A nonempty pymatgen Structure is required.")
        if candidate.composition.reduced_composition != target.reduced_composition:
            raise ValueError("Candidate composition does not match target_formula.")

    @staticmethod
    def _generate_initial_candidate(formula: str) -> Structure:
        """Unimplemented candidate generation must never be disguised as LLM."""
        raise NotImplementedError(
            "No LLM or experimental candidate generator is implemented. "
            "Pass a real pymatgen Structure as initial_structure."
        )

    @staticmethod
    def _perturb_structure_for_retry(
        structure: Structure, iteration: int
    ) -> Structure:
        """Unimplemented refinement must never be disguised as optimization."""
        raise NotImplementedError(
            "No verified feedback-guided proposal/retry engine is installed."
        )

        try:
            checked = float(value)
        except (OverflowError, ValueError) as exc:
            raise RuntimeError(f"Invalid CHGNet {name}.") from exc
        if not math.isfinite(checked) or (nonnegative and checked < 0):
            raise RuntimeError(f"Invalid CHGNet {name}: nonfinite or negative.")
        return checked

    @classmethod
    def _validate_model_result(
        cls, result: Any, candidate: Structure
    ) -> Dict[str, Any]:
        if not isinstance(result, dict):
            raise RuntimeError("Invalid CHGNet result: expected a dictionary.")
        if (
            result.get("engine") != "CHGNet"
            or result.get("execution_status") != "CHGNET_OPTIMIZER_RETURNED_OUTPUT"
            or result.get("model_output_provenance")
            != "MLFF_PREDICTION_NOT_EXPERIMENT"
        ):
            raise RuntimeError("CHGNet result has unverified execution provenance.")
        relaxed = result.get("relaxed_structure")
        if (
            not isinstance(relaxed, Structure)
            or len(relaxed) != len(candidate)
            or relaxed.composition != candidate.composition
        ):
            raise RuntimeError("CHGNet returned an invalid relaxed structure.")
        energy = cls._checked_model_number(
            result.get("potential_energy_ev_per_atom"),
            "potential_energy_ev_per_atom",
        )
        if energy is None:
            raise RuntimeError("CHGNet returned no potential energy.")
        total = cls._checked_model_number(
            result.get("potential_energy_total_ev"),
            "potential_energy_total_ev",
        )
        if total is not None and not math.isclose(
            total, energy * len(relaxed), rel_tol=1e-7, abs_tol=1e-7
        ):
            raise RuntimeError("CHGNet energy totals are inconsistent.")
        max_force = cls._checked_model_number(
            result.get("max_force"), "max_force", nonnegative=True
        )
        min_dist = cls._checked_model_number(
            result.get("min_distance"), "min_distance", nonnegative=True
        )
        # The primary model adapter intentionally leaves these unevaluated.
        # An unexpected non-None value is an unsupported scientific claim.
        unsupported = (
            "e_form", "formation_energy_ev_per_atom", "converged",
            "synthesizability_score", "band_gap_class", "estimated_gap_eV",
            "max_stress", "has_overlap", "ensemble_confidence",
            "is_ensemble_approved",
        )
        if any(result.get(name) is not None for name in unsupported):
            raise RuntimeError("CHGNet output includes unsupported physical claims.")
        return {
            "relaxed": relaxed,
            "potential_energy_ev_per_atom": energy,
            "max_force": max_force,
            "min_dist": min_dist,
        }

    def run_discovery_loop(
        self,
        target_formula: str,
        initial_structure: Optional[Structure] = None,
    ) -> DiscoveryResult:
        """Evaluate zero or one supplied candidate, without synthetic retries.

        If no candidate is supplied, report NOT_RUN. If CHGNet is disabled,
        report NOT_RUN. If it raises, report FAILED. A valid CHGNet output is
        recorded as an unverified MLFF prediction, never a discovery or PASS.
        """
        target = self._parse_target_formula(target_formula)
        canonical_formula = str(target_formula).strip()
        if initial_structure is None:
            return DiscoveryResult(
                target_formula=canonical_formula,
                is_stable=False,
                iterations_taken=0,
                final_structure=None,
                execution_status="NOT_RUN",
                candidate_generation_status="NOT_IMPLEMENTED",
                scientific_interpretation=(
                    "NO MATERIALS DISCOVERY PERFORMED. No candidate structure "
                    "was supplied; autonomous structure generation is not "
                    "implemented. No MLFF, DFT or experimental evidence exists."
                ),
            )
 self._validate_candidate(initial_structure, target)
       if not self.use_mlff:
            return DiscoveryResult(
                target_formula=canonical_formula,
                is_stable=False,
                iterations_taken=0,
                final_structure=None,
                execution_status="NOT_RUN",
                candidate_generation_status="CALLER_SUPPLIED",
                scientific_interpretation=(
                    "A caller-supplied candidate was received, but CHGNet was "
                    "disabled; no relaxation, energy, stability or convergence "
                    "calculation was performed."
                ),
            )

 try:
            raw = self.mlff_validator.evaluate_and_relax(
                initial_structure, fmax=0.1, steps=100
            )
        except Exception as exc:
            return DiscoveryResult(
                target_formula=canonical_formula,
                is_stable=False,
                iterations_taken=1,
                final_structure=None,
                execution_status="FAILED",
                candidate_generation_status="CALLER_SUPPLIED",
                history=[{
                    "iteration": 1,
                    "execution_status": "FAILED",
                    "error_type": type(exc).__name__,
                    "e_form": None,
                    "potential_energy_ev_per_atom": None,
                    "max_force": None,
                    "max_stress": None,
                    "min_dist": None,
                    "has_overlap": None,
                    "severity": "ERROR",
                    "stability_status": "NOT_EVALUATED",
                    "findings": [
                        "CHGNet failed; no model potential energy or "
                        "formation-energy fallback was created."
                    ],
                }],
                scientific_interpretation=(
                    "The requested CHGNet model execution failed. No "
                    "material discovery, stability approval or fabricated "
                    "physical result is reported."
                ),
            )
   checked = self._validate_model_result(raw, initial_structure)
        record = {
            "iteration": 1,
            "execution_status": "CHGNET_OPTIMIZER_RETURNED_OUTPUT",
            "model_output_provenance": "MLFF_PREDICTION_NOT_EXPERIMENT",
            "candidate_provenance": "CALLER_SUPPLIED_NOT_VERIFIED",
            "e_form": None,
            "formation_energy_status": "NOT_CALCULATED",
            "potential_energy_ev_per_atom": checked["potential_energy_ev_per_atom"],
            "max_force": checked["max_force"],
            "max_stress": None,
            "min_dist": checked["min_dist"],
            "has_overlap": None,
            "severity": "INFO",
            "stability_status": "NOT_EVALUATED",
            "convergence_status": "NOT_VERIFIED",
            "is_ensemble_approved": None,
            "retry_status": "NOT_ATTEMPTED_NO_GENERATOR",
            "findings": [
                "One caller-supplied candidate was evaluated by CHGNet.",
                "Potential energy is a model prediction, not formation energy.",
                "No calibrated uncertainty, DFT cross-check, convex-hull "
                "analysis, or experimental stability evidence was obtained.",
                "No autonomous candidate generator or feedback retries ran.",
            ],
        }
return DiscoveryResult(
            target_formula=canonical_formula,
            is_stable=False,
            iterations_taken=1,
            final_structure=checked["relaxed"],
            history=[record],
            execution_status="CHGNET_OPTIMIZER_RETURNED_OUTPUT",
            candidate_generation_status="CALLER_SUPPLIED",
            scientific_interpretation=(
                "A single caller-supplied crystal candidate was evaluated by "
                "CHGNet. The returned potential energy is a model prediction; "
                "no thermodynamic stability, independently verified convergence, "
                "novel materials discovery, or experimental validation is shown."
            ),
        )

# END OF COMPLETE BHS LEGACY ORCHESTRATOR — CHECK THIS LINE ON GITHUB




                    
