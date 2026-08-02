# bhs/reports/generate_artifacts.py

import json
import os
from typing import Dict, Any, List

class PaperArtifactGenerator:
    """
    Generates paper-ready LaTeX tables and benchmark summary reports
    from the 20-System Benchmark JSON outputs.
    """
    
    @staticmethod
    def generate_latex_table(json_path: str, out_tex_path: str = "runs/table1_benchmark.tex") -> str:
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Benchmark output not found at {json_path}")
            
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        latex_lines = [
            "\\begin{table}[h]",
            "\\centering",
            "\\caption{Performance comparison of BHS against Ablation variants and Random Baseline across 20 crystal systems.}",
            "\\label{tab:benchmark_20}",
            "\\begin{tabular}{lcccc}",
            "\\toprule",
            "\\textbf{System} & \\textbf{BHS (Ours)} & \\textbf{No-Bayes} & \\textbf{Fixed-Budget} & \\textbf{Random Search} \\\\",
            "\\midrule"
        ]
        
        for entry in data:
            sys_name = entry["system"]
            m = entry["metrics"]
            bhs_s = m["bhs_full_steps"]
            no_b = m["ablation_no_bayes_steps"]
            fix_b = m["ablation_fixed_budget_steps"]
            rand_s = m["random_baseline_steps"]
            
            line = f"{sys_name} & \\textbf{{{bhs_s}}} & {no_b} & {fix_b} & {rand_s} \\\\"
            latex_lines.append(line)
            
        latex_lines.extend([
            "\\bottomrule",
            "\\end{tabular}",
            "\\end{table}"
        ])
        
        os.makedirs(os.path.dirname(out_tex_path), exist_ok=True)
        with open(out_tex_path, "w", encoding="utf-8") as f:
            f.write("\n".join(latex_lines))
            
        return out_tex_path