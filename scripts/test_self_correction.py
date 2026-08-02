import sys
import os

# Root dizini Python path'ine ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pymatgen.core import Structure, Lattice
from src.imd_pipeline.validation.ensemble_validator import MultiMLFFEnsembleValidator  # CHGNet yerine Ensemble Validator getirildi
from src.imd_pipeline.core.self_correction import AgenticSelfCorrectionEngine

def mock_llm_refinement_fn(prompt: str) -> str:
    """
    LLM API çağrısını simüle eden fonksiyon.
    """
    print("\n🤖 [LLM Agent] Physical feedback received. Refining atomic coordinates...")
    
    cif_refined = """
data_LiFePO4_refined
_cell_length_a       10.33
_cell_length_b       6.01
_cell_length_c       4.69
_cell_angle_alpha    90.00
_cell_angle_beta     90.00
_cell_angle_gamma    90.00
_symmetry_space_group_name_H-M 'P n m a'

loop_
_atom_site_label
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
Li1 0.00000 0.00000 0.00000
Fe1 0.28220 0.25000 0.97470
P1  0.09490 0.25000 0.41820
O1  0.09680 0.25000 0.74240
O2  0.45710 0.25000 0.20600
O3  0.16580 0.04660 0.28470
"""
    return cif_refined

def run_test():
    print("🚀 TESTING AGENTIC SELF-CORRECTION WITH ENSEMBLE VALIDATOR")
    print("==========================================================")

    # 1. Başlangıç bozuk yapısı
    lattice = Lattice.cubic(3.5)
    unstable_structure = Structure(lattice, ["Li", "Fe"], [[0, 0, 0], [0.05, 0.05, 0.05]])
    initial_cif = unstable_structure.to(fmt="cif")

    # 2. Ensemble Validator'ı Başlat
    ensemble_validator = MultiMLFFEnsembleValidator()
    
    # Adaptör: Self-correction engine'e ensemble fonksiyonunu bağlıyoruz
    class EnsembleAdapter:
        def evaluate_and_relax(self, struct):
            return ensemble_validator.evaluate_with_ensemble(struct)

    correction_engine = AgenticSelfCorrectionEngine(validator=EnsembleAdapter(), max_iterations=3)

    # 3. Döngüyü Çalıştır
    result = correction_engine.run_correction_loop(
        initial_cif=initial_cif,
        pymatgen_structure=unstable_structure,
        llm_generate_fn=mock_llm_refinement_fn
    )

    print("\n==========================================================")
    print("🏆 ENSEMBLE SELF-CORRECTION TEST RESULT")
    print("==========================================================")
    print(f"Final Status: {'✅ STABLE' if result.get('converged') else '❌ UNSTABLE'}")
    print(f"Iterations Used: {result.get('iterations_used')}")
    print(f"Final E_form: {result.get('e_form')} eV/atom")
    print(f"Synthesizability Score: {result.get('synthesizability_score')}")
    print(f"Band Gap Class: {result.get('band_gap_class')} ({result.get('estimated_gap_eV')} eV)")
    print(f"Ensemble Confidence: {result.get('ensemble_confidence')}")
    print(f"Ensemble Approved: {result.get('is_ensemble_approved')}")

if __name__ == "__main__":
    run_test()