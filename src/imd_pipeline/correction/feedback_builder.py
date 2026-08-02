from typing import List, Dict, Any
import numpy as np
from pymatgen.core import Structure

class FeedbackBuilder:
    def __init__(self, energy_threshold: float = 0.5, min_dist_threshold: float = 1.2):
        self.energy_threshold = energy_threshold
        self.min_dist_threshold = min_dist_threshold

    def build(self, iteration: int, run_id: str, target_formula: str, findings: List[Any], structure: Structure = None) -> Dict[str, Any]:
        """
        Validation bulgularını ve kristal yapıyı analiz ederek LLM için detaylı düzeltme talimatları üretir.
        """
        critical_issues = []
        actionable_suggestions = []

        # 1. Geometrik Mesafe Kontrolü (Distance Matrix Analysis)
        if structure:
            dist_matrix = structure.distance_matrix
            num_sites = len(structure)
            overlaps = []
            
            for i in range(num_sites):
                for j in range(i + 1, num_sites):
                    d = dist_matrix[i][j]
                    if d < self.min_dist_threshold:
                        site_i = f"{structure[i].species_string}(index={i})"
                        site_j = f"{structure[j].species_string}(index={j})"
                        overlaps.append(f"{site_i} - {site_j}: {d:.2f} Å")
            
            if overlaps:
                critical_issues.append(f"CRITICAL: Atomik çakışma/kritik yakınlık tespit edildi (d < {self.min_dist_threshold} Å): " + ", ".join(overlaps[:3]))
                actionable_suggestions.append(
                    f"Çakışan atomların kesirsel koordinatlarını (fractional coordinates) birbirlerinden uzaklaştıracak şekilde kaydırın. Minimum mesafe en az {self.min_dist_threshold} Å olmalıdır."
                )

        # 2. Validation Engine Bulgu Analizi
        for finding in findings:
            validator_name = getattr(finding, 'validator', '')
            details = getattr(finding, 'details', {})
            severity = str(getattr(finding, 'severity', '')).upper()

            # MLFF Enerji Analizi
            if validator_name == "MLFFValidator" and "e_form" in details:
                e_form = details["e_form"]
                if e_form > self.energy_threshold:
                    critical_issues.append(f"HIGH ENERGY: Tahmini oluşum enerjisi E_form = {e_form:.3f} eV/atom (Eşik: {self.energy_threshold} eV/atom). Yapı kararsız.")
                    actionable_suggestions.append(
                        "Kristal kafes hacmini (unit cell volume) esnetin veya atom bağ uzunluklarını optimize ederek yerel enerji minimumuna yaklaştırın."
                    )

            # Stokiyometri / Şema İhlalleri
            if "CRITICAL" in severity or "ERROR" in severity:
                msg = getattr(finding, 'message', str(finding))
                if msg not in critical_issues:
                    critical_issues.append(f"VALIDATION FAILURE ({validator_name}): {msg}")

        # 3. Structured LLM Correction Prompt Oluşturma
        prompt = f"""
[RETRY ITERATION {iteration}] - Malzeme Üretim Düzeltme Talimatı

Hedef Formül: {target_formula}
Mevcut Durum: Yapı fiziksel/termodinamik doğrulamadan geçemedi.

TESPİT EDİLEN CRITICAL SORUNLAR:
{chr(10).join(['- ' + issue for issue in critical_issues]) if critical_issues else '- Belirli fiziksel parametreler eşik değerlerin dışında.'}

DÜZELTME EYLEM PLANI (ACTIONABLE INSTRUCTIONS):
{chr(10).join(['- ' + sug for sug in actionable_suggestions]) if actionable_suggestions else '- Atomik konumları ve örgü sabitlerini daha kararlı bir konfigürasyona çekin.'}

Lütfen yukarıdaki ihlalleri düzelten Yyeni ve geçerli bir CIF / Structure JSON çıktısı üretin.
"""

        return {
            "run_id": run_id,
            "iteration": iteration,
            "critical_issues": critical_issues,
            "actionable_suggestions": actionable_suggestions,
            "llm_prompt": prompt.strip()
        }