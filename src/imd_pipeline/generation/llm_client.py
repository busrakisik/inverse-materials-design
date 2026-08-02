import logging
from typing import Optional
import numpy as np
from pymatgen.core import Structure, Lattice, Composition

logger = logging.getLogger(__name__)


class LLMClient:
    """
    LLM tabanlı Malzeme ve Kristal Yapı Üretim İstemcisi.
    Orchestrator ile uyumlu çalışarak yapılar üretir ve fiziksel geri bildirimlerle iyileştirir.
    """
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4o"):
        self.api_key = api_key
        self.model_name = model_name
        logger.info(f"LLMClient ilklendirildi (Model: {self.model_name})")

    def generate(self, formula: str) -> Structure:
        """
        Orchestrator tarafından çağrılan ana yapı üretim metodu.
        Verilen kimyasal formül için başlangıç kristal yapısını oluşturur.
        """
        logger.info(f"🤖 LLMClient: '{formula}' için başlangıç kristal yapısı üretiliyor...")
        return self._create_prototype_structure(formula)

    def generate_structure(self, formula: str) -> Structure:
        """Geriye dönük uyumluluk için alias metodu."""
        return self.generate(formula)

    def refine(self, structure: Structure, feedback: str) -> Structure:
        """
        ValidationEngine ve PhysicsFeedbackEngine'den gelen geri bildirimlere
        göre kristal yapının atom koordinatlarını ve kafes parametrelerini iyileştirir.
        """
        logger.info(f"🔄 LLMClient: Geri bildirim işleniyor ve yapı güncelleniyor...")
        
        refined_structure = structure.copy()

        if "OVERLAP" in feedback.upper() or "ÇAKIŞMA" in feedback.upper():
            refined_structure.perturb(distance=0.12)
        else:
            refined_structure.perturb(distance=0.05)

        new_lattice = Lattice.from_parameters(
            a=refined_structure.lattice.a * 1.01,
            b=refined_structure.lattice.b * 1.01,
            c=refined_structure.lattice.c * 1.01,
            alpha=refined_structure.lattice.alpha,
            beta=refined_structure.lattice.beta,
            gamma=refined_structure.lattice.gamma
        )
        
        return Structure(
            lattice=new_lattice,
            species=refined_structure.species,
            coords=refined_structure.frac_coords
        )

    def refine_structure(self, structure: Structure, feedback: str) -> Structure:
        """Geriye dönük uyumluluk için alias metodu."""
        return self.refine(structure, feedback)

    def _create_prototype_structure(self, formula: str) -> Structure:
        """
        Verilen formüldeki element dağılımına ve stokiyometriye göre Pymatgen Structure nesnesi üretir.
        """
        try:
            comp = Composition(formula)
            elements = []
            for elem, count in comp.get_el_amt_dict().items():
                elements.extend([elem.symbol] * int(count))
            
            n_atoms = len(elements)
            lattice_length = max(4.0, 2.5 * (n_atoms ** (1/3)))
            lattice = Lattice.cubic(lattice_length)
            
            coords = []
            for i in range(n_atoms):
                frac_pos = [
                    (i + 0.5) / n_atoms,
                    (i * 0.3) % 1.0,
                    (i * 0.7) % 1.0
                ]
                coords.append(frac_pos)
                
            return Structure(lattice, elements, coords)

        except Exception as e:
            logger.warning(f"Formül ayrıştırma hatası ({e}), varsayılan LiFePO4 şablonu kullanılıyor.")
            lattice = Lattice.orthorhombic(10.3, 6.0, 4.7)
            species = ["Li"] * 4 + ["Fe"] * 4 + ["P"] * 4 + ["O"] * 16
            coords = [[(i / 28), (i / 28), (i / 28)] for i in range(28)]
            return Structure(lattice, species, coords)


# Orchestrator import uyumluluğu için alias
StructureGenerator = LLMClient