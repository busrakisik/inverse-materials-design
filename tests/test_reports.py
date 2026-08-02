# tests/test_reports.py

import os
from bhs.reports.generate_artifacts import PaperArtifactGenerator
from bhs.benchmarks.suite_20 import AblationBenchmarkSuite

def test_paper_artifact_generation():
    # Ensure benchmark data exists
    results = AblationBenchmarkSuite.run_full_suite()
    json_path = AblationBenchmarkSuite.save_benchmark_report(results)
    
    # Generate LaTeX
    tex_path = PaperArtifactGenerator.generate_latex_table(json_path)
    
    assert os.path.exists(tex_path)
    with open(tex_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "\\begin{table}" in content
        assert "LiFePO4" in content
        
    print("\n✅ Paper Artifact & LaTeX Table Generation Test Passed Successfully!")

if __name__ == "__main__":
    test_paper_artifact_generation()