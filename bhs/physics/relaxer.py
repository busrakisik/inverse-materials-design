"""CHGNet relaxation adapter with explicit failures and scientific provenance.

This module distinguishes predicted MLFF energies from experimental measurements,
formation energies, and convex-hull stability metrics.
"""

import math
import time
from typing import Dict, Tuple

from pymatgen.core import Structure

from bhs.provenance.tags import DataProvenanceType, ProvenanceValue


class PhysicsRelaxationEngine:
    """Run a CHGNet relaxation and report its actual predicted outputs.

    If CHGNet is missing or the relaxation fails, this raises an error rather
    than manufacturing an energy value. No stability, formation energy, or
    convex-hull metric is calculated here.
    """

    @staticmethod
    def run_chgnet_relaxation(
        structure: Structure,
    ) -> Tuple[Structure, Dict[str, ProvenanceValue]]:
        if len(structure) == 0:
            raise ValueError("Cannot relax an empty crystal structure.")

        try:
            from chgnet.model.dynamics import StructOptimizer
        except ImportError as exc:
            raise RuntimeError(
                "CHGNet is not installed or cannot be imported. "
                "Install and configure CHGNet before running relaxation. "
                "No energy value has been generated."
            ) from exc

        start_time = time.perf_counter()
        try:
            optimizer = StructOptimizer()
            result = optimizer.relax(structure, fmax=0.05)
            relaxed_structure = result["final_structure"]
            final_total_energy_ev = float(result["trajectory"].energies[-1])
            atom_count = len(relaxed_structure)

            if atom_count == 0 or not math.isfinite(final_total_energy_ev):
                raise ValueError("CHGNet returned an empty structure or non-finite energy.")
        except Exception as exc:
            raise RuntimeError(
                "CHGNet relaxation failed or returned invalid outputs. "
                "No placeholder energy has been substituted."
            ) from exc

        elapsed_seconds = time.perf_counter() - start_time
        potential_energy_per_atom_ev = final_total_energy_ev / atom_count

        results = {
            "potential_energy_per_atom": ProvenanceValue(
                value=potential_energy_per_atom_ev,
                provenance=DataProvenanceType.DERIVED,
                source_description=(
                    "CHGNet-predicted relaxed potential energy per atom (eV/atom); "
                    "NOT formation energy or energy above the convex hull"
                ),
                uncertainty=None,
            ),
            "relaxation_time": ProvenanceValue(
                value=elapsed_seconds,
                provenance=DataProvenanceType.MEASURED,
                source_description="Local wall-clock relaxation time (seconds)",
            ),
            "atom_count": ProvenanceValue(
                value=atom_count,
                provenance=DataProvenanceType.RETRIEVED,
                source_description="Number of sites in CHGNet-relaxed structure",
            ),
        }
        return relaxed_structure, results
