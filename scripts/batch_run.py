import sys
import os
import time
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

# Proje kök dizinini ekle
FILE_PATH = Path(__file__).resolve()
ROOT_DIR = FILE_PATH.parent.parent if FILE_PATH.parent.name == "scripts" else FILE_PATH.parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from imd_pipeline.pipeline.orchestrator import Orchestrator


def run_batch_discovery(
    input_csv: Path,
    output_dir: Path,
    top_n: int = 5,
    e_form_threshold: float = 0.25
) -> pd.DataFrame:
    """
    CSV listesinden kimyasal formülleri okuyarak toplu keşif sürecini başlatır
    ve en kararlı Top-N adayı dışa aktarır.
    """
    print("🚀 ==================================================")
    print("       STARTING BATCH DISCOVERY ENGINE (FAZ 5)")
    print("==================================================\n")

    if not input_csv.exists():
        print(f"⚠️ Warning: Input file {input_csv} not found. Creating a default candidate list...")
        input_csv.parent.mkdir(parents=True, exist_ok=True)
        default_df = pd.DataFrame({
            "formula": ["LiFePO4", "Na3V2(PO4)3", "SrTiO3", "BaTiO3", "LiNiO2", "KFeF3", "Mg2TiO4", "NaFePO4"],
            "target_application": ["Li-Ion", "Na-Ion", "Perovskite", "Piezo", "Li-Ion", "Fluoride", "Mg-Ion", "Na-Ion"]
        })
        default_df.to_csv(input_csv, index=False)

    df_candidates = pd.read_csv(input_csv)
    print(f"📋 Loaded {len(df_candidates)} candidate formulas for batch discovery.\n")

    orchestrator = Orchestrator(
        max_iterations=4,
        e_form_threshold=e_form_threshold,
        use_mlff=True
    )

    batch_results = []
    start_total_time = time.time()

    for idx, row in df_candidates.iterrows():
        formula = row["formula"]
        app_type = row.get("target_application", "General Discovery")
        
        print(f"[{idx+1}/{len(df_candidates)}] 🧪 Processing Formula: {formula} ({app_type})...", end="", flush=True)
        start_time = time.time()

        res = orchestrator.run_discovery_loop(target_formula=formula)
        elapsed = time.time() - start_time

        final_history = res.history[-1] if res.history else {}
        e_form = final_history.get("e_form", 0.0)
        max_force = final_history.get("max_force", 0.0)
        max_stress = final_history.get("max_stress", 0.0)

        batch_results.append({
            "Formula": formula,
            "Application": app_type,
            "Is Stable": "✅ STABLE" if res.is_stable else "❌ UNSTABLE",
            "Formation Energy (eV/atom)": e_form,
            "Max Force (eV/Å)": max_force,
            "Max Stress (GPa)": max_stress,
            "Iterations": res.iterations_taken,
            "Compute Time (s)": round(elapsed, 2)
        })

        print(f" -> E_form: {e_form:.3f} eV/atom | Status: {'✅' if res.is_stable else '❌'} ({elapsed:.2f}s)")

    total_elapsed = time.time() - start_total_time
    df_all_results = pd.DataFrame(batch_results)

    # Top-N Filtreleme ve Sıralama (En Düşük E_form En Üstte)
    df_top_candidates = (
        df_all_results[df_all_results["Is Stable"] == "✅ STABLE"]
        .sort_values(by="Formation Energy (eV/atom)", ascending=True)
        .head(top_n)
    )

    # Çıktıları Kaydetme
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "batch_discovery_summary.csv"
    top_path = output_dir / f"top_{top_n}_stable_materials.csv"

    df_all_results.to_csv(summary_path, index=False)
    df_top_candidates.to_csv(top_path, index=False)

    print("\n==================================================")
    print(f"🎉 Batch Process Completed in {total_elapsed:.2f} seconds!")
    print(f"💾 Full summary saved to: {summary_path}")
    print(f"🏆 Top-{top_n} candidates saved to: {top_path}")
    print("==================================================\n")

    return df_top_candidates


if __name__ == "__main__":
    data_dir = ROOT_DIR / "data"
    output_dir = ROOT_DIR / "outputs"
    input_file = data_dir / "candidate_formulas.csv"

    df_top = run_batch_discovery(
        input_csv=input_file,
        output_dir=output_dir,
        top_n=5,
        e_form_threshold=0.25
    )

    print(f"🏆 TOP-5 DISCOVERED STABLE MATERIALS:")
    print(df_top.to_string(index=False))