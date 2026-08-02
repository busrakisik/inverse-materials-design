import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[3] / "data" / "experiments.db"

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
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

def log_experiment(formula, model_name, prompt_version, validator, e_form, max_force, max_stress, relaxation_time, iterations, is_stable):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO experiment_logs (
            timestamp, formula, model_name, prompt_version, validator, 
            e_form, max_force, max_stress, relaxation_time, iterations, is_stable
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        formula, model_name, prompt_version, validator,
        e_form, max_force, max_stress, relaxation_time, iterations, 1 if is_stable else 0
    ))
    conn.commit()
    conn.close()