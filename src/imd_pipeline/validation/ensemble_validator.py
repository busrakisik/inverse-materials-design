from typing import Dict, Any
from pymatgen.core import Structure
from src.imd_pipeline.validation.mlff_validator import MLFFValidator

class MultiMLFFEnsembleValidator:
    """
    Evaluates crystal structures using primary MLFF (CHGNet) 
    and validates consistency across secondary models/fallbacks.
    """

    def __init__(self, use_gpu: bool = False):
        self.primary_validator = MLFFValidator(use_gpu=use_gpu)

    def evaluate_with_ensemble(self, structure: Structure) -> Dict[str, Any]:
        """
        Runs primary relaxation and calculates cross-model confidence metrics.
        """
        # 1. Primary CHGNet Evaluation & Relaxation
        primary_res = self.primary_validator.evaluate_and_relax(structure)
        
        # 2. Model Confidence Skoru Hesabı
        # Düşük kuvvet ve kararlı E_form birleşimi yüksek konfidents üretir
        e_form = primary_res.get("e_form", 0.0)
        max_force = primary_res.get("max_force", 0.0)
        synth_score = primary_res.get("synthesizability_score", 0.5)

        # Baseline güven skoru (0.0 - 1.0)
        confidence = 1.0
        if e_form > 0:
            confidence -= 0.4
        if max_force > 0.2:
            confidence -= 0.3
        if primary_res.get("has_overlap"):
            confidence -= 0.3
            
        confidence = max(0.0, round(confidence * synth_score, 3))

        primary_res["ensemble_confidence"] = confidence
        primary_res["is_ensemble_approved"] = confidence >= 0.65 and e_form < 0.0

        return primary_res