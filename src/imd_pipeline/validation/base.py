from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
from pymatgen.core import Structure

class Severity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"

@dataclass
class ValidationFinding:
    validator: str
    error_code: str
    severity: Severity
    message: str
    location: Dict[str, Any] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)
    suggested_action: str = ""

class BaseValidator:
    @property
    def name(self) -> str:
        raise NotImplementedError
    def validate(self, structure: Structure) -> list[ValidationFinding]:
        raise NotImplementedError
