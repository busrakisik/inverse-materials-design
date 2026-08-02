def build_correction_prompt(cif_str: str, validation_result: dict) -> str:
    """
    MLFF validator sonuçlarına göre LLM için düzeltme prompt'u oluşturur.
    """
    e_form = validation_result.get("e_form", 0.0)
    max_force = validation_result.get("max_force", 0.0)
    has_overlap = validation_result.get("has_overlap", False)
    min_dist = validation_result.get("min_distance", 0.0)

    feedback_lines = []
    if e_form > 0:
        feedback_lines.append(f"- High Formation Energy: {e_form} eV/atom (Must be negative for thermodynamic stability).")
    if max_force > 0.2:
        feedback_lines.append(f"- Unstable Atomic Forces: Max force is {max_force} eV/A (Target: < 0.1 eV/A). Local atomic positions need relaxation.")
    if has_overlap:
        feedback_lines.append(f"- Severe Atomic Overlap: Minimum interatomic distance is {min_dist} A (Must be > 0.8 A). Adjust Fractional Coordinates.")

    feedback_text = "\n".join(feedback_lines)

    prompt_text = (
        "The previously generated CIF structure exhibited the following physical instabilities during CHGNet MLFF relaxation:\n\n"
        f"{feedback_text}\n\n"
        "### PREVIOUS CIF STRUCTURE:\n"
        "```cif\n"
        f"{cif_str}\n"
        "```\n\n"
        "### INSTRUCTIONS FOR REFINEMENT:\n"
        "1. Adjust atomic fractional coordinates (_atom_site_fract_x, y, z) to eliminate steric overlap and reduce internal stress.\n"
        "2. Maintain space group symmetry while fine-tuning lattice parameters (a, b, c).\n"
        "3. Output ONLY the corrected, valid CIF structure inside a ```cif ... ``` code block."
    )
    
    return prompt_text