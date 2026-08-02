# bhs/provenance/tags.py

from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional

class DataProvenanceType(Enum):
    MEASURED = "Measured"          # Real calculation (CHGNet, ASE, PyMatGen)
    DERIVED = "Derived"            # Mathematical output derived from measured data (Bayes, UCT)
    RETRIEVED = "Retrieved"        # Fetched from DB (Materials Project, CIF files)
    ILLUSTRATIVE = "Illustrative"  # Mock/Demo data explicitly marked for UI visualization

@dataclass
class ProvenanceValue:
    value: Any
    provenance: DataProvenanceType
    source_description: str
    uncertainty: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "provenance": self.provenance.value,
            "source": self.source_description,
            "uncertainty": self.uncertainty
        }

    def __repr__(self) -> str:
        unc_str = f" ± {self.uncertainty}" if self.uncertainty is not None else ""
        return f"{self.value}{unc_str} [{self.provenance.value} | {self.source_description}]"