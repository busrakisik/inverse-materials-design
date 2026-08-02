# tests/test_provenance.py

from bhs.search.bayesian_engine import BayesianHypothesisSearchEngine
from bhs.provenance.tags import DataProvenanceType

def test_bhs_engine_provenance():
    engine = BayesianHypothesisSearchEngine()
    result = engine.accumulate_evidence("Wyckoff Clash Test", {"H1_NASICON": 0.92, "H2_Spinel": 0.65, "H3_Olivine": 0.88})
    
    posterior_h1 = result["posteriors"]["H1_NASICON"]
    
    assert posterior_h1.provenance == DataProvenanceType.DERIVED
    assert "Sequential Bayes" in posterior_h1.source_description
    assert isinstance(posterior_h1.value, float)
    print("\n✅ BHS Engine Provenance Test Passed Successfully!")

if __name__ == "__main__":
    test_bhs_engine_provenance()