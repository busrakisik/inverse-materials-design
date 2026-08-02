from pymatgen.core import Structure
import numpy as np
from typing import Optional, Dict, Any

class PhysicsFeedbackEngine:
    """
    CHGNet relaksasyon çıktılarını ve atomik kuvvetleri analiz ederek 
    LLM/Generator için fizik tabanlı düzeltme yönlendirmeleri (prompt) üretir.
    """
    
    @staticmethod
    def generate_feedback(
        structure: Structure,
        forces: Optional[np.ndarray] = None,
        e_form: float = 0.0,
        iteration: int = 1,
        findings: Optional[list] = None,  # <--- YENİ EKLENEN PARAMETRE
        **kwargs                           # <--- EKSTRA ARGÜMANLARI ESNEK YAKALAMAK İÇİN
    ) -> str:
        """
        Atomik kuvvetleri, enerjiyi ve bulguları (findings) analiz edip LLM'e yönlendirici düzeltme metni hazırlar.
        """
        feedback_lines = [f"--- İTERASYON {iteration} GERİ BİLDİRİMİ ---"]
        
        # Eğer orchestrator'dan 'findings' geldiyse bunları ekle
        if findings:
            feedback_lines.append("Tespit Edilen Sorunlar:")
            for item in findings:
                feedback_lines.append(f"- {item}")
        
        if e_form > 0:
            feedback_lines.append(f"- Oluşum Enerjisi yüksek ({e_form:.3f} eV/atom). Kafes hacmini hafifçe genişlet.")
            
        return "\n".join(feedback_lines)