import os
from typing import Dict, Any, Optional
from pymatgen.core import Structure

class MaterialsProjectEnricher:
    """
    Interfaces with the official Materials Project API (mp-api) 
    to retrieve ground-truth thermodynamic and electronic reference data.
    """

    @staticmethod
    def fetch_reference_metadata(formula: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Queries Materials Project for the lowest energy entry matching the chemical formula.
        """
        # API anahtarını parametreden, çevresel değişkenden veya varsayılan değerden al
        mp_api_key = api_key or os.getenv("MP_API_KEY", "")

        if not mp_api_key:
            # API Key henüz eklenmediyse fallback devrede
            return {
                "database": "Materials Project (Cached / Fallback)",
                "mp_id": "mp-19017 (Cached)",
                "ref_hull_energy_eV": 0.0,
                "ref_e_form": -0.7079,
                "ref_band_gap": 3.7,
                "crystal_system": "Orthorhombic",
                "space_group": "Pnma (62)",
                "provenance_status": "MOCK_FALLBACK (Set MP_API_KEY for live query)"
            }

        try:
            from mp_api.client import MPRester
            
            with MPRester(mp_api_key) as mpr:
                # Formüle göre en kararlı (hull energy'e en yakın) yapıyı sorgula
                docs = mpr.materials.summary.search(
                    formula=formula,
                    fields=["material_id", "energy_above_hull", "formation_energy_per_atom", "band_gap", "symmetry"]
                )
                
                if not docs:
                    return {
                        "database": "Materials Project (Live API)",
                        "mp_id": "NOT_FOUND",
                        "ref_hull_energy_eV": None,
                        "provenance_status": f"No entries found for {formula} in MP."
                    }
                
                # Energy above hull değerine göre sırala ve en stabil olanı al
                best_match = min(docs, key=lambda x: x.energy_above_hull if x.energy_above_hull is not None else 999)
                
                return {
                    "database": "Materials Project (Live API)",
                    "mp_id": str(best_match.material_id),
                    "ref_hull_energy_eV": round(float(best_match.energy_above_hull), 4) if best_match.energy_above_hull is not None else 0.0,
                    "ref_e_form": round(float(best_match.formation_energy_per_atom), 4) if best_match.formation_energy_per_atom is not None else None,
                    "ref_band_gap": round(float(best_match.band_gap), 2) if best_match.band_gap is not None else None,
                    "crystal_system": str(best_match.symmetry.crystal_system) if hasattr(best_match, "symmetry") else "N/A",
                    "space_group": f"{best_match.symmetry.symbol} ({best_match.symmetry.number})" if hasattr(best_match, "symmetry") else "N/A",
                    "provenance_status": "LIVE_API_VERIFIED"
                }

        except Exception as e:
            return {
                "database": f"Materials Project (Error: {type(e).__name__})",
                "mp_id": "mp-19017",
                "ref_hull_energy_eV": 0.0,
                "provenance_status": f"API Error: {str(e)}"
            }