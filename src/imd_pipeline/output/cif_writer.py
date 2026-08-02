from pathlib import Path
from pymatgen.core import Structure

class CIFWriter:
    def write(self, structure: Structure, filepath: Path):
        filepath.parent.mkdir(parents=True, exist_ok=True)
        structure.to(filename=str(filepath), fmt="cif")
