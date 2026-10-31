# BEGIN OF COMPLETE BHS LEGACY MLFF VALIDATOR — CHECK THIS LINE ON GITHUB
"""Explicit CHGNet MLFF adapter, with no synthetic fallback predictions.

A real CHGNet optimizer call may return a predicted potential energy and
observed model force outputs. These are NOT experimentally measured values,
formation energies, calibrated uncertainties, convex-hull stabilities,
synthesizability scores, or band gaps. Tests mock CHGNet; no model is run in CI.

If CHGNet is absent, fails, or returns malformed data, raise an exception.
Never manufacture physics metrics in a fallback branch.
"""

import math
from typing import Any, Dict, Optional

import numpy as np
from pymatgen.core import Structure


class MLFFValidator:
    """Legacy interface for explicit CHGNet predictions, never fake physics."""

    def __init__(self, use_gpu: bool = False):
        if not isinstance(use_gpu, bool):
            raise ValueError("use_gpu must be a boolean.")
        self.use_gpu = use_gpu
        # Avoid loading or downloading model weights during object creation.
        self.model = None
        self.optimizer = None

    @staticmethod
    def _compute_minimum_interatomic_distance(structure: Structure) -> Optional[float]:
        """Minimum periodic pair distance in A; undefined for fewer than 2 sites.

        This is a geometrical observation, not proof of physical stability.
        """
        if not isinstance(structure, Structure) or len(structure) == 0:
            raise ValueError("A nonempty pymatgen Structure is required.")
        if len(structure) < 2:
            return None
        distances = (float(structure.get_distance(i, j))
                     for i in range(len(structure))
                     for j in range(i + 1, len(structure)))
        result = min(distances)
        if not math.isfinite(result) or result < 0.0:
            raise ValueError("Structure returned an invalid pair distance.")
        return result

    @staticmethod
    def _calculate_dynamic_e_form(structure: Structure, raw_energy_per_atom: float):
        """Formation energy cannot be inferred from arbitrary reference offsets."""
        raise NotImplementedError(
            "Formation energy requires a consistent documented elemental "
            "reference scheme and independently validated calculation; "
            "no fallback formation energy can be supplied."
        )

    @staticmethod
    def _fallback_physics_evaluation(structure: Structure):
        """Refuse previous made-up energy/force/stress/band-gap values."""
        raise RuntimeError(
            "Synthetic MLFF fallback disabled. No CHGNet calculation was "
            "performed and no physical output may be reported."
        )

    def evaluate_and_relax(
        self, structure: Structure, fmax: float = 0.1, steps: int = 100
    ) -> Dict[str, Any]:
        """Run the real optional CHGNet optimizer; report provenance clearly.

        Energy is CHGNet-predicted *potential energy per atom* (eV/atom).
        It is NOT an elemental-reference formation energy. The return value
        does not claim convergence, synthesis feasibility, or stability.
        """
        if not isinstance(structure, Structure) or len(structure) == 0:
            raise ValueError("A nonempty pymatgen Structure is required.")
        if isinstance(fmax, bool) or not isinstance(fmax, (int, float)):
            raise ValueError("fmax must be a finite positive number.")
        try:
            checked_fmax = float(fmax)
        except (OverflowError, ValueError) as exc:
            raise ValueError("fmax cannot be represented safely.") from exc
        if not math.isfinite(checked_fmax) or checked_fmax <= 0.0:
            raise ValueError("fmax must be a finite positive number.")
        if isinstance(steps, bool) or not isinstance(steps, int) or steps < 1:
            raise ValueError("steps must be a positive integer.")

        try:
            from chgnet.model.dynamics import StructOptimizer
        except ImportError as exc:
            raise RuntimeError(
                "CHGNet is not installed/importable. No fallback energy or "
                "physical result was generated."
            ) from exc

        try:
            optimizer = StructOptimizer(use_device="cuda" if self.use_gpu else "cpu")
            calculation = optimizer.relax(
                structure, fmax=checked_fmax, steps=steps,
                relax_cell=True, verbose=False,
            )
            relaxed = calculation["final_structure"]
            trajectory = calculation["trajectory"]
            if not isinstance(relaxed, Structure) or len(relaxed) == 0:
                raise ValueError("CHGNet returned no valid relaxed Structure.")
            if len(relaxed) != len(structure):
                raise ValueError("CHGNet returned a different atom count.")
            if relaxed.composition != structure.composition:
                raise ValueError("CHGNet returned a changed chemical composition.")
            energies = trajectory.energies
            if not energies:
                raise ValueError("CHGNet returned no trajectory energies.")
            total_energy_ev = float(energies[-1])
            if not math.isfinite(total_energy_ev):
                raise ValueError("CHGNet returned a nonfinite total energy.")
            per_atom_ev = total_energy_ev / len(relaxed)
            if not math.isfinite(per_atom_ev):
                raise ValueError("CHGNet per-atom potential energy is nonfinite.")

            # Report force vectors only when actually present in the trajectory.
            force_vectors = None
            max_force = None
            observed_forces = getattr(trajectory, "forces", None)
            if observed_forces is not None:
                if len(observed_forces) == 0:
                    raise ValueError("CHGNet returned an empty forces trajectory.")
                vectors = np.asarray(observed_forces[-1], dtype=float)
                if vectors.shape != (len(relaxed), 3) or not np.isfinite(vectors).all():
                    raise ValueError("CHGNet returned invalid final force vectors.")
                max_force = float(np.max(np.linalg.norm(vectors, axis=1)))
                if not math.isfinite(max_force):
                    raise ValueError("CHGNet maximum force is nonfinite.")
                force_vectors = vectors.tolist()

            minimum_distance = self._compute_minimum_interatomic_distance(relaxed)
        except Exception as exc:
            raise RuntimeError(
                "CHGNet execution failed or returned invalid outputs. "
                "No placeholder energy, force, band gap, or convergence "
                "result was substituted."
            ) from exc

        return {
            "relaxed_structure": relaxed,
            "potential_energy_ev_per_atom": per_atom_ev,
            "potential_energy_total_ev": total_energy_ev,
            "raw_energy": None,  # Legacy name ambiguous; use explicit potential_energy keys.
            "e_form": None,
            "formation_energy_ev_per_atom": None,
            "max_force": max_force,
            "max_stress": None,
            "min_distance": minimum_distance,
            "has_overlap": None,  # Geometry alone is not a validated overlap classifier.
            "synthesizability_score": None,
            "band_gap_class": None,
            "estimated_gap_eV": None,
            "forces": force_vectors,
            "stress_tensor": None,
            "converged": None,  # Optimization termination is not verified convergence.
            "engine": "CHGNet",
            "device_requested": "cuda" if self.use_gpu else "cpu",
            "execution_status": "CHGNET_OPTIMIZER_RETURNED_OUTPUT",
            "model_output_provenance": "MLFF_PREDICTION_NOT_EXPERIMENT",
            "independent_verification_status": "NOT_VERIFIED",
            "formation_energy_status": "NOT_CALCULATED",
            "band_gap_status": "NOT_CALCULATED",
            "convergence_status": "NOT_VERIFIED",
            "scientific_interpretation": (
                "CHGNet optimizer returned a model-predicted potential energy. "
                "No formation energy, convex-hull stability, synthesis score, "
                "band gap, independently verified convergence, or empirical "
                "material property is established by this result."
            ),
        }
# END OF COMPLETE BHS LEGACY MLFF VALIDATOR — CHECK THIS LINE ON GITHUB
