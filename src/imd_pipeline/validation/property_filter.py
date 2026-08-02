import numpy as np
from pymatgen.core import Structure

class PropertyFilter:
    """
    Evaluates functional physical properties and synthesizability metrics for inorganic crystals.
    """

    @staticmethod
    def estimate_synthesizability(structure: Structure) -> float:
        """
        Kristal yapısının sentezlenebilirlik skorunu (0.0 - 1.0) hesaplar.
        Skor; atomlar arası mesafe homojenliği ve simetri faktörüne dayanır.
        """
        if len(structure) < 2:
            return 0.5

        dist_matrix = structure.distance_matrix
        np.fill_diagonal(dist_matrix, np.inf)
        min_dists = np.min(dist_matrix, axis=1)

        # Anormal kısa veya aşırı uzun bağların mevcudiyeti skoru düşürür
        dist_std = float(np.std(min_dists))
        avg_dist = float(np.mean(min_dists))

        if avg_dist < 1.0:
            return 0.1  # Steric overlap riski çok yüksek
        
        # Homojen bağ dağılımı yüksek sentezlenebilirlik göstergesidir
        score = 1.0 - min(0.8, (dist_std / (avg_dist + 1e-5)))
        return round(float(score), 3)

    @staticmethod
    def classify_band_gap(structure: Structure, e_form: float) -> dict:
        """
        Element bileşimi ve oluşum enerjisine göre bant aralığı tahmini yapar.
        """
        comp = structure.composition
        elements = [el.symbol for el in comp.elements]

        # Metaller (Transition Metals yoğunluklu ve düşük O/F içeriği)
        has_metals = any(el in ["Fe", "Ni", "Co", "V", "Ti", "Cu", "Zn"] for el in elements)
        has_anions = any(el in ["O", "F", "S", "N", "P"] for el in elements)

        if has_metals and not has_anions:
            gap_type = "Metallic"
            est_gap = 0.0
        elif has_anions and ("O" in elements or "F" in elements):
            if e_form < -2.0:
                gap_type = "Insulator"
                est_gap = 3.5
            else:
                gap_type = "Semiconductor"
                est_gap = 1.8
        else:
            gap_type = "Semiconductor"
            est_gap = 1.2

        return {
            "band_gap_class": gap_type,
            "estimated_gap_eV": est_gap
        }