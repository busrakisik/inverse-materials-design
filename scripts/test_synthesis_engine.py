import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pymatgen.core import Structure, Lattice
from src.imd_pipeline.synthesis.recipe_generator import AutonomousSynthesisEngine

def main():
    print("🧪 TESTING AUTONOMOUS SYNTHESIS RECIPE GENERATOR")
    print("================================================")

    # Örnek LiFePO4 kristali
    lattice = Lattice.orthorhombic(10.33, 6.01, 4.69)
    struct = Structure(lattice, ["Li", "Fe", "P", "O"], [[0,0,0], [0.28,0.25,0.97], [0.09,0.25,0.41], [0.09,0.25,0.74]])

    recipe = AutonomousSynthesisEngine.generate_recipe(struct, e_form=-2.3983)

    print(f"🎯 Target Material: {recipe['target_formula']}")
    print(f"🔬 Selected Precursors: {', '.join(recipe['precursors'])}")
    print(f"🔥 Sintering Temperature: {recipe['sintering_temp_C']} °C ({recipe['atmosphere']})")
    print(f"📊 Synthesis Difficulty: {recipe['synthesis_difficulty']}")
    print("\n📋 Experimental Protocol Steps:")
    for step in recipe['synthesis_steps']:
        print(f"  {step}")

if __name__ == "__main__":
    main()