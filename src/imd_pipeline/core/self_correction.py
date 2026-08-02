from typing import Dict, Any
from src.imd_pipeline.validation.mlff_validator import MLFFValidator
from src.imd_pipeline.prompts.physics_feedback import build_correction_prompt

class AgenticSelfCorrectionEngine:
    def __init__(self, validator: MLFFValidator, max_iterations: int = 3):
        self.validator = validator
        self.max_iterations = max_iterations

    def run_correction_loop(self, initial_cif: str, pymatgen_structure, llm_generate_fn) -> Dict[str, Any]:
        """
        Geri besleme döngüsü: MLFF fiziksel hatalarını LLM'e ileterek CIF yapısını iyileştirir.
        """
        current_cif = initial_cif
        current_structure = pymatgen_structure
        history = []

        for iteration in range(1, self.max_iterations + 1):
            print(f"\n🔄 [Self-Correction Iteration {iteration}/{self.max_iterations}] Evaluating Structure...")
            
            # 1. Physical Validation
            val_result = self.validator.evaluate_and_relax(current_structure)
            history.append({
                "iteration": iteration,
                "e_form": val_result["e_form"],
                "max_force": val_result["max_force"],
                "converged": val_result["converged"]
            })

            # 2. Kararlılık Kriteri Kontrolü ($E_{form} < 0$ ve max_force < 0.25)
            if val_result["e_form"] <= 0.0 and val_result["max_force"] <= 0.25 and not val_result["has_overlap"]:
                print(f"✅ Physical Stability Achieved at Iteration {iteration}!")
                val_result["iterations_used"] = iteration
                val_result["correction_history"] = history
                return val_result

            print(f"⚠️ Stability Check Failed (E_form: {val_result['e_form']} eV/atom, Max Force: {val_result['max_force']} eV/Å). Constructing Feedback...")

            # 3. Build Prompt & LLM Refinement Call
            feedback_prompt = build_correction_prompt(current_cif, val_result)
            
            # LLM'den yeni CIF talep et (Mock veya Gerçek LLM çağrısı)
            new_cif = llm_generate_fn(feedback_prompt)
            if not new_cif:
                print("❌ LLM failed to return a revised CIF. Aborting loop.")
                break
                
            current_cif = new_cif
            # Pymatgen yapısını güncelle (Parse CIF)
            try:
                from pymatgen.core import Structure
                current_structure = Structure.from_str(current_cif, fmt="cif")
            except Exception as e:
                print(f"❌ Failed to parse refined CIF: {e}")
                break

        val_result["iterations_used"] = len(history)
        val_result["correction_history"] = history
        return val_result