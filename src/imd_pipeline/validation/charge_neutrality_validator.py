from __future__ import annotations
from pymatgen.core import Structure
from pymatgen.analysis.bond_valence import BVAnalyzer
from imd_pipeline.validation.base import BaseValidator, ValidationFinding, Severity

class ChargeNeutralityValidator(BaseValidator):
    def __init__(self, tolerance: float = 1e-2):
        self.tolerance = tolerance

    @property
    def name(self) -> str:
        return "charge_neutrality_validator"

    def validate(self, structure: Structure) -> list[ValidationFinding]:
        findings = []
        try:
            bva = BVAnalyzer()
            valences = bva.get_valences(structure)
            net_charge = float(sum(valences))
            
            if abs(net_charge) > self.tolerance:
                findings.append(
                    ValidationFinding(
                        validator=self.name,
                        error_code="CHARGE_IMBALANCE",
                        severity=Severity.CRITICAL,
                        message=f"Yapı net olarak yük-nötr değil. Net yük: {net_charge:+.2f}",
                        details={"computed_net_charge": net_charge},
                        suggested_action="Stokiyometriyi ve atom sayılarını yeniden dengele."
                    )
                )
        except Exception:
            findings.append(
                ValidationFinding(
                    validator=self.name,
                    error_code="VALENCE_ASSIGNMENT_FAILED",
                    severity=Severity.WARNING,
                    message="Oksidasyon durumu atanamadı.",
                    suggested_action="Bağ mesafelerini makul sınırlar içine çek."
                )
            )
        return findings
