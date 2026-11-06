"""Safe legacy compatibility interface for literature and patent assessment.

IMPORTANT: This module DOES NOT access Materials Project, OQMD, Crossref,
arXiv, publication indexes, or patent databases. It performs no similarity
search or novelty evaluation. No patent clearance, freedom-to-operate finding,
confidence score, or scientific novelty percentage can be inferred here.

The class name is retained ONLY to avoid breaking legacy import statements.
Implement a separately tested source-retrieval pipeline, citation trail, and
human claim review before reporting real search or patent conclusions.
"""

from typing import Any, Dict


class RealLiteraturePatentAgent:
    """Legacy name; deliberately makes NO claim of real literature searches."""

    @staticmethod
    def evaluate_novelty(formula: str, structure_fingerprint: str) -> Dict[str, Any]:
        """Report a non-executed assessment; never fabricate results.

        Both arguments are identifiers supplied by the caller, not evidence
        of a validated chemical formula or a calculated structure descriptor.
        """
        if not isinstance(formula, str) or not formula.strip():
            raise ValueError("formula must be a nonempty string.")
        if not isinstance(structure_fingerprint, str) or not structure_fingerprint.strip():
            raise ValueError("structure_fingerprint must be a nonempty string.")

        return {
            "formula": formula.strip(),
            "structure_fingerprint": structure_fingerprint.strip(),
            "input_provenance": "CALLER_SUPPLIED_NOT_VERIFIED",
            "formula_validation_status": "NOT_VERIFIED",
            "structure_fingerprint_validation_status": "NOT_VERIFIED",
            "novelty_assessment_status": "NOT_EVALUATED",
            "novelty_score": None,
            "closest_known_material": None,
            "known_polymorph": None,
            "confidence": None,
            "data_sources_consulted": [],
            "source_checks": {
                "Materials Project": "NOT_RUN",
                "OQMD": "NOT_RUN",
                "Crossref": "NOT_RUN",
                "arXiv": "NOT_RUN",
                "Patent databases": "NOT_RUN",
            },
            "patent_prior_art": {
                "status": "NOT_CHECKED",
                "closest_patent": None,
                "claim_overlap_probability": None,
                "patent_claims_reviewed": 0,
                "jurisdictions_checked": [],
                "freedom_to_operate": "NOT_ASSESSED",
            },
            "scientific_interpretation": (
                "NO SEARCH OR NOVELTY ASSESSMENT PERFORMED. "
                "Caller-supplied identifiers were not independently checked. "
                "No publications, structures, polymorphs, or patents were "
                "retrieved or compared. Novelty and patent clearance are "
                "unknown; professional freedom-to-operate review would be "
                "needed for legal conclusions."
            ),
        }

