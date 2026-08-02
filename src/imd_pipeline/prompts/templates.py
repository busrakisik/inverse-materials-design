from typing import Dict, Any, Optional


class PromptTemplates:
    """
    Malzeme Keşfi için A/B Testi Prompt Stratejileri.
    """

    @staticmethod
    def get_prompt_a(formula: str) -> str:
        """Prompt A: Direct / Naive Baseline"""
        return f"""Generate a valid CIF (Crystallographic Information File) structure for the material formula: {formula}.
Output ONLY the raw CIF block without any conversational text."""

    @staticmethod
    def get_prompt_b(formula: str, space_group: str = "Pnma") -> str:
        """Prompt B: Symmetry & Space Group Constrained"""
        return f"""You are a materials crystallographer. Generate a stable unit cell CIF for the chemical formula: {formula}.
Enforce the space group symmetry: {space_group}.
Ensure fractional coordinates respect Wyckoff positions and realistic ionic radii to prevent overlapping atoms.
Output strictly valid CIF data."""

    @staticmethod
    def get_prompt_c(formula: str, physics_feedback: Optional[Dict[str, Any]] = None) -> str:
        """Prompt C: Physics-Feedback Closed-Loop (A/B Testing Star)"""
        if not physics_feedback:
            return PromptTemplates.get_prompt_b(formula)

        min_dist = physics_feedback.get("min_dist", 0.0)
        e_form = physics_feedback.get("e_form", 0.0)
        max_force = physics_feedback.get("max_force", 0.0)

        return f"""The previously generated structure for {formula} was evaluated by CHGNet MLFF and found UNSTABLE:
- Minimum interatomic distance: {min_dist:.2f} Å (CRITICAL: Atomic overlap detected!)
- Current Formation Energy: {e_form:.3f} eV/atom (Target: < 0.25 eV/atom)
- Max Forces: {max_force:.3f} eV/Å

PHYSICS INSTRUCTIONS FOR REFUSION:
1. Increase the lattice cell parameters (a, b, c) by 2-5% to decrease packing density.
2. Perturb fractional coordinates along high-stress bonds to eliminate interatomic overlap.
3. Maintain charge neutrality and symmetry constraints.

Generate the corrected CIF structure now."""