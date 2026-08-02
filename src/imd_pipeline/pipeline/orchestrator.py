import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pymatgen.core import Structure, Lattice

from imd_pipeline.validation.mlff_validator import MLFFValidator


@dataclass
class DiscoveryResult:
    """Discovery loop çıktısını ve geçmişini tutan veri sınıfı."""
    target_formula: str
    is_stable: bool
    iterations_taken: int
    final_structure: Optional[Structure]
    history: List[Dict[str, Any]] = field(default_factory=list)


class Orchestrator:
    """
    Closed-Loop Material Discovery Orchestrator.
    LLM Jeneratörü ile CHGNet Physics Validator arasındaki kapalı döngü
    fiziksel optimizasyon sürecini yönetir.
    """

    def __init__(
        self,
        max_iterations: int = 5,
        e_form_threshold: float = 0.25,
        use_gpu: bool = False,
        use_mlff: bool = True
    ):
        self.max_iterations = max_iterations
        self.e_form_threshold = e_form_threshold
        self.use_mlff = use_mlff
        self.mlff_validator = MLFFValidator(use_gpu=use_gpu)

    def _generate_initial_candidate(self, formula: str) -> Structure:
        """
        Başlangıç aday kristal yapısını üretir.
        (LLM API entegrasyonu buraya bağlanır, şimdilik sentetik başlangıç yapısı döner).
        """
        # LiFePO4 için Orthorhombic Pnma sentetik başlangıç kafesi
        lattice = Lattice.orthorhombic(10.33, 6.01, 4.69)
        species = ["Li", "Fe", "P", "O", "O", "O", "O"]
        coords = [
            [0.00, 0.00, 0.00],
            [0.28, 0.25, 0.97],
            [0.09, 0.25, 0.41],
            [0.09, 0.25, 0.74],
            [0.45, 0.25, 0.20],
            [0.16, 0.04, 0.28],
            [0.16, 0.46, 0.28]
        ]
        return Structure(lattice, species, coords)

    def _perturb_structure_for_retry(self, structure: Structure, iteration: int) -> Structure:
        """
        LLM feedback simülasyonu: Bir önceki adımda çakışma/yüksek enerji varsa
        kristal parametrelerini genleşmeye ve koordinatları perturb etmeye zorlar.
        """
        new_lattice = structure.lattice.scale(structure.volume * (1.0 + 0.02 * iteration))
        new_coords = []
        for site in structure.sites:
            # Koordinatlara küçük rastgele kaydırmalar ekle (Perturbation)
            shift = (iteration * 0.01) % 0.05
            new_coords.append([site.a + shift, site.b - shift, site.c + shift])
            
        return Structure(new_lattice, structure.species, new_coords)

    def run_discovery_loop(self, target_formula: str) -> DiscoveryResult:
        """
        Otonom kapalı döngü keşif sürecini başlatır.

        1. Aday yapıyı oluştur (LLM Generator)
        2. CHGNet ile relakse et ve fiziksel metrikleri hesapla (Validator)
        3. Enerji eşiğini ve atomik çakışmaları kontrol et
        4. Uygun değilse fiziksel yönlendirme (Decision Engine) ile döngüyü tekrar et
        """
        history = []
        current_structure = self._generate_initial_candidate(target_formula)
        is_stable = False
        final_structure = None

        for iteration in range(1, self.max_iterations + 1):
            # 1. Real CHGNet Physics Evaluation & Force-Field Relaxation
            if self.use_mlff:
                validation_res = self.mlff_validator.evaluate_and_relax(
                    current_structure, 
                    fmax=0.1, 
                    steps=100
                )
                relaxed_struct = validation_res["relaxed_structure"]
                e_form = validation_res["e_form"]
                max_force = validation_res["max_force"]
                max_stress = validation_res["max_stress"]
                min_dist = validation_res["min_distance"]
                has_overlap = validation_res["has_overlap"]
                engine_used = validation_res["engine"]
            else:
                # MLFF kapalıysa fallback basit hesaplama
                relaxed_struct = current_structure
                min_dist = self.mlff_validator._compute_minimum_interatomic_distance(current_structure)
                has_overlap = min_dist < 0.8
                e_form = 0.35 if has_overlap else 0.18
                max_force = 0.50 if has_overlap else 0.05
                max_stress = 1.80 if has_overlap else 0.10
                engine_used = "Basic Fallback"

            # 2. Decision Engine Evaluation (Kararlılık Eşiği Kontrolü)
            is_energy_ok = e_form <= self.e_form_threshold
            is_physically_valid = not has_overlap and is_energy_ok
            
            severity = "PASS" if is_physically_valid else ("CRITICAL" if has_overlap else "WARN")

            # 3. İzlenebilirlik Logu (History Entry for UI Decision Trace)
            findings = [
                f"Engine: {engine_used}",
                f"Minimum interatomic distance: {min_dist:.3f} Å",
                f"Max Force Vector: {max_force:.4f} eV/Å",
                f"Max Stress Tensor: {max_stress:.4f} GPa",
                f"Formation Energy: {e_form:.4f} eV/atom (Threshold: {self.e_form_threshold} eV/atom)"
            ]

            history_entry = {
                "iteration": iteration,
                "e_form": e_form,
                "max_force": max_force,
                "max_stress": max_stress,
                "min_dist": min_dist,
                "has_overlap": has_overlap,
                "severity": severity,
                "findings": findings
            }
            history.append(history_entry)

            # 4. Durdurma Kriteri (Convergence check)
            if is_physically_valid:
                is_stable = True
                final_structure = relaxed_struct
                break

            # 5. Yakınsama sağlanamadıysa yeni iterasyon için prompt/yapı güncelle
            current_structure = self._perturb_structure_for_retry(relaxed_struct, iteration)
            final_structure = relaxed_struct

        return DiscoveryResult(
            target_formula=target_formula,
            is_stable=is_stable,
            iterations_taken=len(history),
            final_structure=final_structure,
            history=history
        )