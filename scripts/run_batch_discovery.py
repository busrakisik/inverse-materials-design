import sys
import os
import sqlite3
import json
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pymatgen.core import Structure, Lattice
from src.imd_pipeline.validation.ensemble_validator import MultiMLFFEnsembleValidator
from src.imd_pipeline.synthesis.recipe_generator import AutonomousSynthesisEngine

def init_db(db_path="data/experiments.db"):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS discovery_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            formula TEXT,
            e_form REAL,
            synthesizability_score REAL,
            band_gap_class TEXT,
            ensemble_confidence REAL,
            approved BOOLEAN,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_result(data: dict, db_path="data/experiments.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO discovery_results (formula, e_form, synthesizability_score, band_gap_class, ensemble_confidence, approved, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data["formula"],
        data["e_form"],
        data["synthesizability_score"],
        data["band_gap_class"],
        data["ensemble_confidence"],
        data["approved"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def run_batch():
    print("🚀 STARTING AUTONOMOUS BATCH DISCOVERY SIMULATION")
    print("==================================================")
    
    init_db()
    validator = MultiMLFFEnsembleValidator()

    # Tarama yapılacak aday malzeme listesi (Stokiometri & Kafes yapıları)
    candidates = [
        {"formula": "LiFePO4", "lattice": Lattice.orthorhombic(10.33, 6.01, 4.69), "species": ["Li", "Fe", "P", "O"], "coords": [[0,0,0], [0.28,0.25,0.97], [0.09,0.25,0.41], [0.09,0.25,0.74]]},
        {"formula": "NaFePO4", "lattice": Lattice.orthorhombic(10.40, 6.10, 4.75), "species": ["Na", "Fe", "P", "O"], "coords": [[0,0,0], [0.28,0.25,0.97], [0.09,0.25,0.41], [0.09,0.25,0.74]]},
        {"formula": "BaTiO3",  "lattice": Lattice.cubic(4.01), "species": ["Ba", "Ti", "O"], "coords": [[0,0,0], [0.5,0.5,0.5], [0.5,0.5,0.0]]},
        {"formula": "LiCoO2",  "lattice": Lattice.hexagonal(2.81, 14.05), "species": ["Li", "Co", "O"], "coords": [[0,0,0], [0,0,0.5], [0,0,0.23]]}
    ]

    for item in candidates:
        print(f"\n🔬 Processing Candidate: {item['formula']}...")
        struct = Structure(item["lattice"], item["species"], item["coords"])
        
        # 1. Ensemble Validation & Physical Relaxation
        eval_res = validator.evaluate_with_ensemble(struct)
        
        # 2. Reçete Motoru
        recipe = AutonomousSynthesisEngine.generate_recipe(struct, eval_res.get("e_form", 0.0))
        
        record = {
            "formula": item["formula"],
            "e_form": eval_res.get("e_form"),
            "synthesizability_score": eval_res.get("synthesizability_score"),
            "band_gap_class": eval_res.get("band_gap_class"),
            "ensemble_confidence": eval_res.get("ensemble_confidence"),
            "approved": eval_res.get("is_ensemble_approved")
        }
        
        # 3. DB Kayıt
        save_result(record)
        print(f"  └─ Status: {'✅ APPROVED' if record['approved'] else '❌ REJECTED'} | E_form: {record['e_form']} eV/atom | Confidence: {record['ensemble_confidence']}")

    print("\n==================================================")
    print("🏆 BATCH DISCOVERY COMPLETED & SAVED TO SQLite DB!")

if __name__ == "__main__":
    run_batch()