
"""Explicitly heuristic structural evidence scores for the BHS prototype.

These functions DO NOT estimate calibrated probabilities P(E | H), validate
Wyckoff positions, calculate SOAP descriptors, or establish crystal stability.
They return dimensionless, uncalibrated heuristic scores. A calibrated evidence
model must be developed before using these as scientific Bayesian likelihoods.
"""

import math

from pymatgen.core import Structure

from bhs.provenance.tags import DataProvenanceType, ProvenanceValue


def _finite_number(name: str, value, *, minimum: float = 0.0, strict: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite numeric value.")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite.")
    if number <= minimum if strict else number < minimum:
        operator = ">" if strict else ">="
        raise ValueError(f"{name} must be {operator} {minimum}.")
    return number


class LikelihoodEngine:
    """Calculate uncalibrated scores (legacy method names kept for compatibility)."""

    @staticmethod
    def calculate_wyckoff_clash_likelihood(
        structure: Structure,
        eta: float = 0.75,
        lambda_clash: float = 10.0,
    ) -> ProvenanceValue:
        """Heuristic periodic hard-sphere overlap score, NOT a Wyckoff likelihood.

        For every neighboring periodic atom pair below eta*(r_i+r_j), apply
        exp[-lambda_clash * sum(overlap_fraction**2)]. Neighbor lists count
        each pair twice, so their summed penalty is divided by two. This is
        uncalibrated: a score near 1 does not imply physical stability.
        """
        eta = _finite_number("eta", eta, strict=True)
        lambda_clash = _finite_number("lambda_clash", lambda_clash)
        if not isinstance(structure, Structure) or not len(structure):
            raise ValueError("structure must be a nonempty pymatgen Structure.")

        radii = []
        for index, site in enumerate(structure.sites):
            try:
                radius = site.specie.atomic_radius
                radius = float(radius) if radius is not None else None
            except (AttributeError, TypeError, ValueError) as exc:
                raise ValueError(
                    f"Atomic radius unavailable for site {index}; cannot score overlaps."
                ) from exc
            if radius is None or not math.isfinite(radius) or radius <= 0:
                raise ValueError(
                    f"Atomic radius unavailable for site {index}; cannot score overlaps."
                )
            radii.append(radius)

        # Include periodic images, including same-site images when sufficiently
        # close; looking only at pairs within the unit cell would miss clashes.
        max_overlap_distance = 2.0 * eta * max(radii)
        neighbors_per_site = structure.get_all_neighbors(
            r=max_overlap_distance,
            include_index=True,
        )
        penalty_twice = 0.0
        for site_index, neighbors in enumerate(neighbors_per_site):
            for neighbor in neighbors:
                neighbor_index = int(neighbor.index)
                distance = float(neighbor.nn_distance)
                if not math.isfinite(distance) or distance < 0:
                    raise ValueError("Invalid interatomic distance in neighbor list.")
                threshold = eta * (radii[site_index] + radii[neighbor_index])
                if distance < threshold:
                    overlap_fraction = 1.0 - (distance / threshold)
                    penalty_twice += overlap_fraction ** 2

        score = math.exp(-lambda_clash * penalty_twice / 2.0)
        return ProvenanceValue(
            value=score,
            provenance=DataProvenanceType.DERIVED,
            source_description=(
                "UNCALIBRATED heuristic periodic hard-sphere overlap score "
                "computed from supplied structure and atomic radii; "
                "NOT a measured Bayesian likelihood, Wyckoff validation, "
                "or thermodynamic stability assessment"
            ),
            uncertainty=None,
        )

    @staticmethod
    def calculate_soap_novelty_likelihood(
        soap_distance: float,
        delta: float = 0.5,
    ) -> ProvenanceValue:
        """Map a supplied SOAP distance to a heuristic score, NOT a likelihood.

        Does NOT calculate a SOAP descriptor or validate whether the caller's
        distance is a meaningful SOAP distance. Scores are not calibrated.
        """
        soap_distance = _finite_number("soap_distance", soap_distance)
        delta = _finite_number("delta", delta, strict=True)
        score = -math.expm1(-soap_distance / delta)
        return ProvenanceValue(
            value=score,
            provenance=DataProvenanceType.DERIVED,
            source_description=(
                "UNCALIBRATED novelty score transformed from caller-supplied "
                "SOAP distance; SOAP distance provenance NOT verified; "
                "NOT a measured Bayesian likelihood"
            ),
            uncertainty=None,
        )

