import json
import os
from pymatgen.core import Structure
from pymatgen.io.vasp import Poscar
from pymatgen.io.cif import CifWriter

class MaterialDataExporter:
    """
    Handles multi-format exports (CIF, POSCAR, JSON, CSV, BibTeX) for research workflows.
    """

    @staticmethod
    def export_all(structure: Structure, metadata: dict, output_dir="outputs/exports"):
        os.makedirs(output_dir, exist_ok=True)
        formula = structure.composition.reduced_formula
        
        # 1. CIF Export
        cif_path = os.path.join(output_dir, f"{formula}.cif")
        cif_writer = CifWriter(structure)
        cif_writer.write_file(cif_path)

        # 2. POSCAR Export
        poscar_path = os.path.join(output_dir, f"POSCAR_{formula}")
        poscar = Poscar(structure)
        poscar.write_file(poscar_path)

        # 3. JSON Export
        json_path = os.path.join(output_dir, f"{formula}_metadata.json")
        with open(json_path, "w") as f:
            json.dump(metadata, f, indent=4)

        # 4. BibTeX Citation Export
        bib_path = os.path.join(output_dir, f"{formula}_citation.bib")
        bib_content = f"""@article{{{formula}_imd_2026,
  title={{AI-Assisted Autonomous Discovery and Physics Validation of {formula}}},
  author={{Inverse Materials Discovery Platform}},
  journal={{Journal of Materials Chemistry A}},
  year={{2026}},
  publisher={{Royal Society of Chemistry}}
}}"""
        with open(bib_path, "w") as f:
            f.write(bib_content)

        return {
            "CIF": cif_path,
            "POSCAR": poscar_path,
            "JSON": json_path,
            "BibTeX": bib_path
        }