# tests/test_benchmarks.py

from bhs.benchmarks.baselines import RandomSearchBaseline, BenchmarkRunner
from bhs.provenance.tags import DataProvenanceType

def test_benchmark_baselines():
    candidates = ["LiFePO4_Olivine", "LiFePO4_Spinel", "LiFePO4_NASICON"]
    
    # 1. Random Search Test
    random_engine = RandomSearchBaseline(candidates)
    res_random = random_engine.run_step()
    assert res_random["selected_candidate"] in candidates
    assert res_random["probability"].provenance == DataProvenanceType.DERIVED

    # 2. Benchmark Comparison Test
    bench = BenchmarkRunner(targets=["LiFePO4", "Na3V2(PO4)3", "SrTiO3"])
    eval_res = bench.evaluate_system("LiFePO4")
    
    assert eval_res["target"] == "LiFePO4"
    assert eval_res["bhs_steps_to_converge"] < eval_res["random_steps_to_converge"]
    print("\n✅ Benchmark & Baseline Integration Test Passed Successfully!")

if __name__ == "__main__":
    test_benchmark_baselines()