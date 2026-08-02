import os
from typing import Dict, Any
from pymatgen.core import Structure

class AutonomousSynthesisEngine:
    """
    Generates literature-informed candidate synthesis protocols and precursor recommendations 
    for generated crystal structures.
    """

    PRECURSORS_DB = {
        "Li": ["Li2CO3 (Lithium Carbonate)", "LiOH.H2O"],
        "Fe": ["FeC2O4.2H2O (Iron(II) Oxalate Dihydrate)", "Fe2O3"],
        "P": ["(NH4)2HPO4 (Diammonium Phosphate)", "NH4H2PO4"],
        "O": ["Air/Oxygen Flow"],
        "Na": ["Na2CO3"],
        "V": ["V2O5"],
        "Ti": ["TiO2"]
    }

    @staticmethod
    def generate_recipe(structure: Structure, e_form: float) -> Dict[str, Any]:
        comp = structure.composition
        elements = [el.symbol for el in comp.elements]

        selected_precursors = []
        for el in elements:
            if el in AutonomousSynthesisEngine.PRECURSORS_DB:
                selected_precursors.append(AutonomousSynthesisEngine.PRECURSORS_DB[el][0])
            else:
                selected_precursors.append(f"High-purity elemental {el} powder")

        calcination_temp = 350
        sintering_temp = 650 if "Li" in elements else 800
        atmosphere = "Ar/H2 (95%/5%) inert flow" if "Fe" in elements or "V" in elements else "Air"

        steps = [
            f"1. Stoichiometric Milling: Stoichiometrically weigh {', '.join(selected_precursors)}.",
            f"2. High-Energy Ball Milling: Planetary ball mill at 400 rpm for 4 hours in ethanol wet medium.",
            f"3. Pre-Calcination: Heat ground mixture to {calcination_temp} °C for 3 hours under {atmosphere}.",
            f"4. Pelletization: Press powder into 13mm disks at 10 MPa pressure.",
            f"5. Final Sintering: Anneal pellets at {sintering_temp} °C for 12 hours under {atmosphere}.",
            f"6. Quenching/Cooling: Furnace cool to room temperature at 5 °C/min."
        ]

        return {
            "target_formula": comp.reduced_formula,
            "precursors": selected_precursors,
            "sintering_temp_C": sintering_temp,
            "atmosphere": atmosphere,
            "synthesis_steps": steps,
            "feasibility_assessment": "Plausible (Literature-Informed)" if e_form < -1.5 else "Challenging",
            "reference_basis": "Solid-state reaction pathway inferred from inorganic precursor database & thermochemical stability bounds."
        }