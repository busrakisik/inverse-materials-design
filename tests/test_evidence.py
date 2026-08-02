# tests/test_evidence.py

from pymatgen.core import Structure, Lattice
from bhs.evidence.likelihoods import LikelihoodEngine
from bhs.provenance.tags import DataProvenanceType

def test_evidence_likelihoods():
    lattice = Lattice.cubic(4.0)
    # Standard cubic structure
    struct = Structure(lattice, ["Li", "F"], [[0, 0, 0], [0.5, 0.5, 0.5]])
    
    l_wyckoff = LikelihoodEngine.calculate_wyckoff_clash_likelihood(struct)
    l_novelty = LikelihoodEngine.calculate_soap_novelty_likelihood(soap_distance=0.42)
    
    assert l_wyckoff.provenance == DataProvenanceType.MEASURED
    assert 0.0 <= l_wyckoff.value <= 1.0
    assert l_novelty.provenance == DataProvenanceType.DERIVED
    print("\n✅ Evidence Engine Likelihood Test Passed Successfully!")

if __name__ == "__main__":
    test_evidence_likelihoods()