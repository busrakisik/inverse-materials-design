import json
from typing import Dict, Any, Tuple
from pymatgen.core import Structure

class AgenticSelfCorrectionEngine:
    """
    Translates physical validation errors (forces, clashes, energy)
    into structured LLM prompts to iteratively refine candidate crystal structures.
    """

    @staticmethod
    def generate_refinement_prompt(validation_result: Dict[str, Any], attempt: int) -> str:
        """
        Builds a structured prompt payload for the generator LLM based on validator output.
        """
        feedback_payload = {
            "attempt": attempt,
            "status": "REJECTED_NEEDS_CORRECTION",
            "detected_issues": [],
            "required_adjustments": []
        }

        # Force Threshold Check
        if validation_result.get("max_force", 0) > 0.10:
            feedback_payload["detected_issues"].append(
                f"High internal force detected: f_max = {validation_result['max_force']} eV/Å (threshold: 0.10 eV/Å)"
            )
            feedback_payload["required_adjustments"].append(
                "Apply atomic position displacement along force gradient or relax lattice vectors."
            )

        # Steric Clash Check
        if validation_result.get("has_overlap", False):
            feedback_payload["detected_issues"].append(
                f"Steric hindrance/clash detected. Interatomic distance ({validation_result.get('min_distance')} Å) below threshold."
            )
            feedback_payload["required_adjustments"].append(
                "Expand unit cell volume by 1.5% - 3.0% and adjust Wyckoff site coordinates."
            )

        prompt = f"""
SYSTEM ROLE: Senior Crystallographer & Physics Refinement Agent

VALIDATION FEEDBACK (Attempt {attempt}):
{json.dumps(feedback_payload, indent=2)}

INSTRUCTION:
Modify the candidate structure parameters to satisfy energy minimization constraints.
Return the updated lattice parameters (a, b, c, alpha, beta, gamma) and fractional coordinates in valid JSON format.
"""
        return prompt

    @staticmethod
    def inspect_and_correct(validation_result: Dict[str, Any], attempt: int = 1) -> Dict[str, Any]:
        """
        Simulates / executes the agentic self-correction pass.
        """
        prompt = AgenticSelfCorrectionEngine.generate_refinement_prompt(validation_result, attempt)
        
        return {
            "prompt_sent": prompt,
            "correction_applied": True,
            "next_attempt": attempt + 1
        }