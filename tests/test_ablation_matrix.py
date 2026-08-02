# tests/test_ablation_matrix.py

import os
from bhs.benchmarks.suite_20 import AblationBenchmarkSuite

def test_20_system_ablation_suite():
    results = AblationBenchmarkSuite.run_full_suite()
    
    # 20 sistemin tamamı tarandı mı?
    assert len(results) == 20
    
    # BHS, Ablation ve Random'dan daha az adımda çözüme ulaştı mı?
    for r in results:
        m = r["metrics"]
        assert m["bhs_full_steps"] < m["ablation_no_bayes_steps"]
        assert m["bhs_full_steps"] < m["random_baseline_steps"]
        
    out_file = AblationBenchmarkSuite.save_benchmark_report(results)
    assert os.path.exists(out_file)
    print("\n✅ 20-System Benchmark & Ablation Matrix Test Passed Successfully!")

if __name__ == "__main__":
    test_20_system_ablation_suite()