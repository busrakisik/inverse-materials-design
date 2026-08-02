from __future__ import annotations
from pymatgen.core import Structure
from imd_pipeline.validation.base import BaseValidator, ValidationFinding, Severity

class OverlapValidator(BaseValidator):
    def __init__(self, min_distance_ratio: float = 0.7):
        self.min_distance_ratio = min_distance_ratio

    @property
    def name(self) -> str:
        return "overlap_validator"

    def validate(self, structure: Structure) -> list[ValidationFinding]:
        findings = []
        for i, site1 in enumerate(structure):
            for j, site2 in enumerate(structure):
                if i >= j:
                    continue
                dist = site1.distance(site2)
                r1 = site1.specie.atomic_radius or 1.0
                r2 = site2.specie.atomic_radius or 1.0
                min_allowed = (r1 + r2) * self.min_distance_ratio
                if dist < min_allowed:
                    findings.append(
                        ValidationFinding(
                            validator=self.name,
                            error_code="ATOM_OVERLAP",
                            severity=Severity.CRITICAL,
                            message=f"{site1.specie.symbol} ve {site2.specie.symbol} atomları aşırı yakın ({dist:.2f} Å).",
                            location={"atom_indices": [i, j], "species": [site1.specie.symbol, site2.specie.symbol]},
                            details={"actual_distance": dist, "min_allowed": min_allowed},
                            suggested_action="Fraksiyonel koordinatları atomlar arası mesafeyi artıracak şekilde güncelle."
                        )
                    )
        return findings
