"""Integration checks for the BHS illustrative CLI demo.

These tests do NOT reconstruct crystal structures or validate materials.
They verify that the Bayesian demonstration is explicitly opt-in and that its
run records correctly indicate an unverified, non-physical computation.
"""

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from bhs.cli import run_pipeline


CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs" / "reconstruction_lifepo4.yaml"


def _load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_physical_pipeline_is_not_falsely_claimed():
    """Calling the API without --demo must not produce discovery artifacts."""
    with TemporaryDirectory() as folder:
        target = Path(folder) / "not_a_discovery"
        try:
            run_pipeline(str(CONFIG_PATH), str(target))
        except ValueError as exc:
            assert "--demo" in str(exc)
        else:
            raise AssertionError("Unverified physical reconstruction must be refused")
        assert not target.exists()


def test_demo_records_are_explicitly_illustrative_and_unverified():
    """Run the real CLI demo and inspect recorded data and file hashes."""
    with TemporaryDirectory() as folder:
        target = Path(folder) / "demo"
        saved = Path(run_pipeline(str(CONFIG_PATH), str(target), demo=True))
        assert saved == target

        config = _load_json(saved / "input_config.json")
        history = _load_json(saved / "execution_history.json")
        manifest = _load_json(saved / "provenance_manifest.json")

        assert config["mode"] == "ILLUSTRATIVE_DEMO_NOT_VERIFIED"
        assert config["likelihood_source"] == "HARDCODED_ILLUSTRATIVE_VALUES"
        assert config["MLFF_executed"] is False
        assert config["physical_constraints_applied"] is False
        assert config["search_budget_allocated"] is False
        assert config["target_composition"] == "LiFePO4"

        assert manifest["artifact_type"] == "BHS_RUN_RECORD"
        assert manifest["reproducibility_status"] == "NOT_VERIFIED"
        assert manifest["verification_status"] == "NOT_VERIFIED"
        assert manifest["final_metrics"]["status"] == "DEMO_ONLY_NOT_VERIFIED"
        assert manifest["final_metrics"]["energy_ev_per_atom"] is None
        assert manifest["final_metrics"]["GPU_hours_measured"] is None
        assert manifest["final_metrics"]["materials_discovered"] is None

        assert len(history) == 1
        assert history[0]["evidence_provenance"] == "ILLUSTRATIVE"
        assert history[0]["physical_validation"] == "NOT_RUN"
        assert history[0]["gpu_hours_allocated"] is None
        posteriors = history[0]["posteriors"]
        assert set(posteriors) == set(config["source_configuration"]["priors"])
        assert all(0 <= value <= 1 for value in posteriors.values())
        assert abs(sum(posteriors.values()) - 1.0) < 0.001

        for filename in ("input_config.json", "execution_history.json"):
            actual_hash = hashlib.sha256((saved / filename).read_bytes()).hexdigest()
            assert manifest["files"][filename]["sha256"] == actual_hash


def test_invalid_priors_do_not_create_a_run():
    """Invalid input must fail before saving misleading artifacts."""
    invalid_config = """target_composition: LiFePO4
priors:
  H1_Olivine_Pnma: 0.50
  H2_Spinel_Fd3m: 0.50
  H3_NASICON_R3c: 0.50
"""
    with TemporaryDirectory() as folder:
        config_path = Path(folder) / "invalid.yaml"
        config_path.write_text(invalid_config, encoding="utf-8")
        target = Path(folder) / "must_not_exist"
        try:
            run_pipeline(str(config_path), str(target), demo=True)
        except ValueError as exc:
            assert "sum to 1.0" in str(exc)
        else:
            raise AssertionError("Invalid priors must not be accepted")
        assert not target.exists()


if __name__ == "__main__":
    test_physical_pipeline_is_not_falsely_claimed()
    test_demo_records_are_explicitly_illustrative_and_unverified()
    test_invalid_priors_do_not_create_a_run()
    print("PASS: 3 illustrative CLI integration checks; no physics was run")
