
# BEGIN OF COMPLETE BHS LEGACY PHYSICS SAFETY SHIM — CHECK THIS LINE ON GITHUB
"""Fail-closed guard for an unaudited legacy Streamlit physics interface.

The previous implementation manufactured 32 optimization steps, energies,
forces, DFT scores, convergence status and provenance hashes without running
CHGNet, ASE or DFT. Those outputs must NOT be described as calculations.

This compatibility module intentionally does not emit simulation results.
For an optional actual CHGNet adapter, see bhs.physics.relaxer. The legacy
Streamlit app must be redesigned and independently tested before reenabling
any physics display. This module intentionally causes the old demo path to
stop rather than display fictional scientific evidence.
"""

import hashlib
from typing import Any, Dict, Tuple


class RealPhysicsEngine:
    """Legacy class name retained so callers receive a transparent failure."""

    @staticmethod
    def generate_sha256(content: str) -> str:
        """Return a content digest, not a claim of simulation or verification.

        Retain this general utility for older callers. Hashing arbitrary
        input does not demonstrate that any physical calculation took place.
        """
        if not isinstance(content, str):
            raise TypeError("content must be a string.")
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def run_chgnet_relaxation(structure: Any) -> Tuple[Any, Dict[str, Any]]:
        """Refuse to simulate a real CHGNet run using invented metrics.

        This deprecated legacy API previously produced fake optimization logs,
        a fixed 'formation energy', fabricated DFT scores and success status.
        It is intentionally disabled until the Streamlit UI is refactored to
        consume independently verified outputs from a real calculation.

        No numerical result, run log or fake provenance is generated.
        """
        raise NotImplementedError(
            "LEGACY PHYSICS PATH DISABLED: the former RealPhysicsEngine "
            "fabricated CHGNet relaxation steps, energy/force histories, "
            "DFT scores and convergence/provenance metadata. "
            "No real simulation was performed by this legacy API. "
            "Do not report those values as measured or predicted physics. "
            "Use bhs.physics.relaxer.PhysicsRelaxationEngine only for "
            "an explicitly configured, actual CHGNet run. "
            "The old Streamlit app needs a separate safe-UI update."
        )

# END OF COMPLETE BHS LEGACY PHYSICS SAFETY SHIM — CHECK THIS LINE ON GITHUB

