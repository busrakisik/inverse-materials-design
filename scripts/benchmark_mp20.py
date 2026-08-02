import os
import sys
import time
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Proje kök dizinini sys.path'e ekle
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Pipeline, Inspector ve Logger Importları
try:
    from imd_pipeline.pipeline.orchestrator import Orchestrator
    from imd_pipeline.tracker.db_logger import log_experiment
except ImportError:
    # Lokal paket import düşüşü (fall-back)
    from src.imd_pipeline.pipeline.orchestrator import Orchestrator
    from src.imd_pipeline.tracker.db_logger import log_experiment


# -----------------------------------------------------------------------------
# DB Initialization Helper
# -----------------------------------------------------------------------------
def init_benchmark_db():
    """Ensure SQLite database table exists for historical tracking."""
    db_path = ROOT_DIR / "data" / "experiments.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiment_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            formula TEXT,
            model_name TEXT,
            prompt_version TEXT,
            validator TEXT,
            e_form REAL,
            max_force REAL,
            max_stress REAL,
            relaxation_time REAL,
            iterations INTEGER,
            is_stable INTEGER
        )
    """)
    conn.commit()
    conn.close()


# -----------------------------------------------------------------------------
# Benchmark Main Runner
# -----------------------------------------------------------------------------
def run_mp20_benchmark(num_samples: int = 20, model_name: str = "Qwen-2.5-72B", prompt_ver: str = "v4_physics"):
    """
    Executes real MP-20 structural validation across target candidates.
    Calculates E_form MAE, force convergence, and updates SQLite DB logs.
    """
    print("=" * 70)
    print("🚀 STARTING REAL MP-20 BENCHMARK EXECUTION")
    print(f"📊 Target Samples: {num_samples} | Model: {model_name} | Prompt: {prompt_ver}")
    print("=" * 70)

    init_benchmark_db()

    # MP-20 Referans Aday Listesi (Batarya, Perovskit ve Oksit Katotlar)
    mp20_candidates = [
        {"formula": "LiFePO4", "application": "Li-Ion Cathode", "ref_e_form": -1.85},
        {"formula": "Na3V2(PO4)3", "application": "Na-Ion Cathode", "ref_e_form": -2.10},
        {"formula": "SrTiO3", "application": "Perovskite Solar", "ref_e_form": -3.20},
        {"formula": "BaTiO3", "application": "Piezoelectric", "ref_e_form": -3.12},
        {"formula": "LiNiO2", "application": "Li-Ion High-Capacity", "ref_e_form": -1.45},
        {"formula": "KFeF3", "application": "Fluoride Battery", "ref_e_form": -2.30},
        {"formula": "Mg2TiO4", "application": "Multivalent Battery", "ref_e_form": -2.25},
        {"formula": "NaFePO4", "application": "Sodium Battery", "ref_e_form": -1.72},
        {"formula": "CaTiO3", "application": "Perovskite Dielectric", "ref_e_form": -3.05},
        {"formula": "ZnO", "application": "Semiconductor Optoelectronics", "ref_e_form": -1.60},
        {"formula": "LiMn2O4", "application": "Spinel Battery Cathode", "ref_e_form": -1.90},
        {"formula": "Al2O3", "application": "Structural Ceramic", "ref_e_form": -3.40},
        {"formula": "TiO2", "application": "Photocatalyst", "ref_e_form": -3.00},
        {"formula": "Fe2O3", "application": "Energy Storage Oxide", "ref_e_form": -1.95},
        {"formula": "SiC", "application": "Power Electronics", "ref_e_form": -0.65},
        {"formula": "GaN", "application": "Wide Bandgap Semi", "ref_e_form": -1.10},
        {"formula": "Li4Ti5O12", "application": "Anode Material", "ref_e_form": -2.40},
        {"formula": "NaCoO2", "application": "Na-Ion Battery", "ref_e_form": -1.30},
        {"formula": "La2CuO4", "application": "Superconductor Oxide", "ref_e_form": -2.15},
        {"formula": "CsPbI3", "application": "Halide Perovskite Solar", "ref_e_form": -0.85}
    ]

    selected_samples = mp20_candidates[:min(num_samples, len(mp20_candidates))]
    
    orchestrator = Orchestrator(
        max_iterations=4,
        e_form_threshold=0.25,
        use_mlff=True,
        use_gpu=False
    )

    benchmark_logs = []
    total_start_time = time.time()

    for idx, item in enumerate(selected_samples, start=1):
        formula = item["formula"]
        app_domain = item["application"]
        ref_e_form = item["ref_e_form"]

        print(f"\n[{idx}/{len(selected_samples)}] 🧪 Testing Candidate: {formula} ({app_domain})")
        t_sample_start = time.time()

        # Closed-Loop Discovery Loop Çağrısı
        res = orchestrator.run_discovery_loop(target_formula=formula)
        sample_elapsed = time.time() - t_sample_start

        # Fizik Metriklerini Çekme
        final_hist = res.history[-1] if res.history else {}
        calc_e_form = final_hist.get("e_form", 0.0)
        max_force = final_hist.get("max_force", 0.0)
        max_stress = final_hist.get("max_stress", 0.0)
        mae_e_form = abs(calc_e_form - ref_e_form)

        # 1. SQLite Veritabanına Gerçek Deney Kaydı Yapma
        try:
            log_experiment(
                formula=formula,
                model_name=model_name,
                prompt_version=prompt_ver,
                validator="CHGNet",
                e_form=calc_e_form,
                max_force=max_force,
                max_stress=max_stress,
                relaxation_time=round(sample_elapsed, 3),
                iterations=res.iterations_taken,
                is_stable=res.is_stable
            )
        except Exception as db_err:
            print(f"⚠️ DB Logging Warning for {formula}: {db_err}")

        # Summary Log Dizisi
        benchmark_logs.append({
            "Formula": formula,
            "Application": app_domain,
            "Is Stable": "✅ PASS" if res.is_stable else "❌ FAIL",
            "Ref E_form": ref_e_form,
            "Calc E_form (eV/atom)": calc_e_form,
            "E_form MAE": round(mae_e_form, 4),
            "Max Force (eV/Å)": round(max_force, 4),
            "Max Stress (GPa)": round(max_stress, 4),
            "Relaxation Time (s)": round(sample_elapsed, 2),
            "Iterations": res.iterations_taken
        })

        print(f"    ├─ Status: {'✅ CONVERGED' if res.is_stable else '❌ UNSTABLE'}")
        print(f"    ├─ E_form: {calc_e_form:.3f} eV/atom (Ref: {ref_e_form:.2f} | MAE: {mae_e_form:.3f})")
        print(f"    └─ Time: {sample_elapsed:.2f}s | Iterations: {res.iterations_taken}")

    total_elapsed = time.time() - total_start_time
    df_results = pd.DataFrame(benchmark_logs)

    # -------------------------------------------------------------------------
    # Özet İstatistikleri Hesaplama & Kaydetme
    # -------------------------------------------------------------------------
    pass_rate = (df_results["Is Stable"] == "✅ PASS").mean() * 100
    avg_mae = df_results["E_form MAE"].mean()
    avg_time = df_results["Relaxation Time (s)"].mean()

    outputs_dir = ROOT_DIR / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    
    csv_out_path = outputs_dir / "mp20_benchmark_results.csv"
    df_results.to_csv(csv_out_path, index=False)

    print("\n" + "=" * 70)
    print("🏆 MP-20 BENCHMARK SUMMARY & METRICS")
    print("=" * 70)
    print(f"📊 Total Candidates Evaluated : {len(df_results)}")
    print(f"✅ Pass Rate (Thermodynamic Stability) : {pass_rate:.1f}%")
    print(f"🎯 Formation Energy Mean Absolute Error (MAE): {avg_mae:.4f} eV/atom")
    print(f"⚡ Average Relaxation Time per Material    : {avg_time:.2f} seconds")
    print(f"⏱️ Total Execution Time                   : {total_elapsed:.2f} seconds")
    print(f"📂 Full Report Saved To                   : {csv_out_path}")
    print("=" * 70)


if __name__ == "__main__":
    # Varsayılan 10 aday ile benchmark'ı başlat
    run_mp20_benchmark(num_samples=10)