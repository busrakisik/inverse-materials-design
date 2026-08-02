# bhs/evidence/likelihoods.py

import math
from typing import Dict, Any
from pymatgen.core import Structure
from bhs.provenance.tags import ProvenanceValue, DataProvenanceType

class LikelihoodEngine:
    """
    Computes rigorous physical & structural likelihoods L(E_k | H_i)
    under the Naive Bayesian conditional independence assumption.
    """
    
    @staticmethod
    def calculate_wyckoff_clash_likelihood(structure: Structure, eta: float = 0.75, lambda_clash: float = 10.0) -> ProvenanceValue:
        """
        Calculates hard-sphere atomic overlap likelihood L_wyckoff.
        L = exp(-lambda * sum(max(0, 1 - d_ij / (eta * (r_i + r_j)))^2))
        """
        clash_penalty = 0.0
        sites = structure.sites
        
        for i in range(len(sites)):
            for j in range(i + 1, len(sites)):
                dist = sites[i].distance(sites[j])
                r_i = sites[i].specie.atomic_radius or 1.2
                r_j = sites[j].specie.atomic_radius or 1.2
                min_allowed = eta * (r_i + r_j)
                
                if dist < min_allowed:
                    clash_penalty += (1.0 - (dist / min_allowed)) ** 2
                    
        likelihood = math.exp(-lambda_clash * clash_penalty)
        
        return ProvenanceValue(
            value=round(likelihood, 4),
            provenance=DataProvenanceType.MEASURED,
            source_description="Hard-sphere atomic radius overlap calculation",
            uncertainty=0.01
        )

    @staticmethod
    def calculate_soap_novelty_likelihood(soap_distance: float, delta: float = 0.5) -> ProvenanceValue:
        """
        Calculates novelty likelihood based on SOAP Kernel Distance.
        L_novelty = 1 - exp(-min_dist / delta)
        """
        likelihood = 1.0 - math.exp(-soap_distance / delta)
        
        return ProvenanceValue(
            value=round(likelihood, 4),
            provenance=DataProvenanceType.DERIVED,
            source_description="SOAP (Smooth Overlap of Atomic Positions) Kernel Distance Likelihood"
        )