from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

class StructureAnalyzer:
    """
    Üretilen CIF dosyalarını analiz eder: Hücre boyutları, uzay grubu ve atomik bağ mesafelerini çıkarır.
    """
    def __init__(self, cif_path: Path):
        self.cif_path = cif_path
        self.structure = Structure.from_file(str(cif_path))

    def get_summary(self) -> Dict[str, Any]:
        lattice = self.structure.lattice
        sga = SpacegroupAnalyzer(self.structure, symprec=0.1)

        # Atomlar arası bağ mesafeleri (en yakın komşular)
        bond_distances: List[Dict[str, Any]] = []
        for i, site1 in enumerate(self.structure):
            for j, site2 in enumerate(self.structure):
                if i < j:
                    dist = float(site1.distance(site2))
                    if dist < 4.0: # Sadece 4.0 Å altındaki fiziksel bağları al
                        bond_distances.append({
                            "pair": f"{site1.specie.symbol} - {site2.specie.symbol}",
                            "indices": [i, j],
                            "distance_angstrom": round(dist, 3)
                        })

        return {
            "cif_path": str(self.cif_path),
            "formula": self.structure.composition.reduced_formula,
            "num_sites": len(self.structure),
            "lattice_parameters": {
                "a": round(lattice.a, 3),
                "b": round(lattice.b, 3),
                "c": round(lattice.c, 3),
                "alpha": round(lattice.alpha, 2),
                "beta": round(lattice.beta, 2),
                "gamma": round(lattice.gamma, 2),
                "volume": round(lattice.volume, 3)
            },
            "spacegroup": {
                "number": sga.get_space_group_number(),
                "symbol": sga.get_space_group_symbol(),
                "crystal_system": sga.get_crystal_system()
            },
            "close_bonds": sorted(bond_distances, key=lambda x: x["distance_angstrom"])[:10]
        }
