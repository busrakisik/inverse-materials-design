from __future__ import annotations
from typing import Optional
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from imd_pipeline.validation.base import BaseValidator, ValidationFinding, Severity

class SymmetryValidator(BaseValidator):
    def __init__(self, symprec: float = 0.1):
        self.symprec = symprec

    @property
    def name(self) -> str:
        return "symmetry_validator"

    def validate(self, structure: Structure, target_spacegroup: Optional[int] = None) -> list[ValidationFinding]:
        findings = []
        try:
            sga = SpacegroupAnalyzer(structure, symprec=self.symprec)
            detected_sg_num = sga.get_space_group_number()
            detected_sg_symbol = sga.get_space_group_symbol()

            if target_spacegroup is not None and detected_sg_num != target_spacegroup:
                findings.append(
                    ValidationFinding(
                        validator=self.name,
                        error_code="SPACEGROUP_MISMATCH",
                        severity=Severity.CRITICAL,
                        message=f"Hedef uzay grubu ({target_spacegroup}) ile tespit edilen ({detected_sg_num} - {detected_sg_symbol}) uyuşmuyor.",
                        location={"atom_indices": [], "species": [], "wyckoff_site": None},
                        details={"expected_spacegroup": target_spacegroup, "detected_spacegroup_number": detected_sg_num},
                        suggested_action="Atom pozisyonlarını uzay grubu simetri operatörlerine uyacak şekilde ayarla."
                    )
                )
        except Exception as e:
            findings.append(
                ValidationFinding(
                    validator=self.name,
                    error_code="SYMMETRY_ANALYSIS_FAILED",
                    severity=Severity.CRITICAL,
                    message=f"Simetri analizi hatası: {str(e)}",
                    suggested_action="Birim hücre parametrelerini ve fraksiyonel koordinatları kontrol et."
                )
            )
        return findings
