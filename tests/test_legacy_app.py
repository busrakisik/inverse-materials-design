# BEGIN OF COMPLETE BHS STREAMLIT APP SAFETY TESTS — CHECK THIS LINE ON GITHUB
"""Scoped BHS app software/provenance tests; NOT scientific materials validation.

The real mathematical Bayesian updater and real pymatgen CIF parser are used
in CI. Streamlit is replaced with a recording UI; CHGNet is never loaded or run.
These checks do not show measured performance, discovery, physical stability,
verified thermodynamic formation energy, experimental validation or DFT.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import types
from contextlib import nullcontext

import pytest
from pymatgen.core import Lattice, Structure


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


class _UploadedCIF:
    def __init__(self, data):
        self._data = data

    def getvalue(self):
        return self._data


class _RecordingUI(types.ModuleType):
    """Fake Streamlit boundary that never makes network or MLFF calls."""

    def __init__(self):
        super().__init__("streamlit")
        self.events = []
        self.session_state = {}
        self.upload = None
        self.consent = False
        self.press = False

    def _record(self, name, args, kwargs):
        self.events.append((name, args, kwargs))

    def __getattr__(self, name):
        def call(*args, **kwargs):
            self._record(name, args, kwargs)
            if name == "file_uploader":
                return self.upload
            if name == "checkbox":
                return self.consent
            if name == "button":
                return self.press and not kwargs.get("disabled", False)
            if name == "tabs":
                return [nullcontext() for _ in args[0]]
            if name in ("spinner", "expander"):
                return nullcontext()
            return None

        return call

    def calls(self, name):
        return [(args, kwargs) for name0, args, kwargs in self.events if name0 == name]


@pytest.fixture
def ui_app(monkeypatch):
    """Load app without installing Streamlit or invoking the page entrypoint."""
    ui = _RecordingUI()
    monkeypatch.setitem(sys.modules, "streamlit", ui)
    spec = importlib.util.spec_from_file_location(
        "bhs_ui_app_test_loaded", APP_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return ui, module


@pytest.fixture
def cif_bytes():
    structure = Structure(
        Lattice.cubic(4.0),
        ["Li", "O"],
        [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]],
    )
    return structure.to(fmt="cif").encode("utf-8")


def _model_result(state="CHGNET_OPTIMIZER_RETURNED_OUTPUT", energy=-3.25):
    record = {
        "iteration": 1,
        "e_form": None,
        "potential_energy_ev_per_atom": energy,
        "stability_status": "NOT_EVALUATED",
        "formation_energy_status": "NOT_CALCULATED",
    }
    return types.SimpleNamespace(
        execution_status=state,
        stability_status="NOT_EVALUATED",
        convergence_status="NOT_VERIFIED",
        history=[record] if state == "CHGNET_OPTIMIZER_RETURNED_OUTPUT" else [],
        scientific_interpretation="MLFF model prediction, not stability proof.",
    )


def _install_orchestrator(monkeypatch, app, result=None, failure=None):
    """Capture calls instead of importing or executing CHGNet weights."""
    records = []
    response = result if result is not None else _model_result()

    class FakeOrchestrator:
        def __init__(self, **kwargs):
            records.append(("init", kwargs))

        def run_discovery_loop(self, *, target_formula, initial_structure):
            records.append(("run", target_formula, initial_structure))
            if failure is not None:
                raise failure
            return response

    monkeypatch.setattr(app, "Orchestrator", FakeOrchestrator)
    return records


def _run_uploaded(ui, app, data, *, consent=False, press=False):
    ui.upload = _UploadedCIF(data)
    ui.consent = consent
    ui.press = press
    app._render_optional_chgnet()


def test_app_path_points_to_repo_root():
    assert APP_PATH.name == "app.py"
    assert APP_PATH.parent.joinpath("bhs", "cli.py").is_file()


def test_app_import_does_not_call_streamlit_render_functions(ui_app):
    ui, _app = ui_app
    assert ui.events == []


def test_app_exposes_only_explicit_main_entrypoint(ui_app):
    ui, app = ui_app
    assert callable(app.main)
    assert not ui.calls("set_page_config")
    assert not ui.calls("tabs")


def test_demo_is_identified_as_illustrative(ui_app):
    _, app = ui_app
    result = app.calculate_illustrative_bayesian_demo()
    assert result["mode"] == "ILLUSTRATIVE_DEMO_NOT_PHYSICAL_EVIDENCE"


@pytest.mark.parametrize("key", [
    "input_prior_provenance", "input_likelihood_provenance",
])
def test_demo_declares_hardcoded_input_provenance(ui_app, key):
    _, app = ui_app
    assert app.calculate_illustrative_bayesian_demo()[key] == (
        "HARDCODED_ILLUSTRATIVE_VALUES"
    )


@pytest.mark.parametrize("field,expected", [
    ("physical_evidence_status", "NOT_VERIFIED"),
    ("model_execution_status", "NOT_RUN"),
    ("bayesian_likelihood_calibration_status", "NOT_VERIFIED"),
    ("stability_status", "NOT_EVALUATED"),
    ("discovery_status", "NOT_DEMONSTRATED"),
])
def test_demo_explicitly_rejects_scientific_certification(ui_app, field, expected):
    _, app = ui_app
    assert app.calculate_illustrative_bayesian_demo()[field] == expected


@pytest.mark.parametrize("field", [
    "gpu_hours_allocated", "formation_energy_ev_per_atom", "band_gap_eV"
])
def test_demo_has_no_fabricated_physical_numbers(ui_app, field):
    _, app = ui_app
    assert app.calculate_illustrative_bayesian_demo()[field] is None


def test_demo_has_no_fictitious_mcts_rollouts(ui_app):
    _, app = ui_app
    assert app.calculate_illustrative_bayesian_demo()["mcts_rollouts_executed"] is False


def test_demo_priors_are_normalized(ui_app):
    _, app = ui_app
    result = app.calculate_illustrative_bayesian_demo()
    assert math.fsum(result["input_priors"].values()) == pytest.approx(1.0)


def test_demo_posteriors_are_normalized(ui_app):
    _, app = ui_app
    result = app.calculate_illustrative_bayesian_demo()
    assert math.fsum(result["mathematical_posteriors"].values()) == pytest.approx(1.0)


def test_demo_hypothesis_sets_are_consistent(ui_app):
    _, app = ui_app
    result = app.calculate_illustrative_bayesian_demo()
    assert (set(result["input_priors"])
            == set(result["input_likelihoods"])
            == set(result["mathematical_posteriors"]))


@pytest.mark.parametrize("hypothesis", [
    "H1_Olivine_Pnma", "H2_Spinel_Fd3m", "H3_NASICON_R3c"
])
def test_demo_bayes_posteriors_match_explicit_arithmetic(ui_app, hypothesis):
    _, app = ui_app
    result = app.calculate_illustrative_bayesian_demo()
    weights = {
        key: prior * result["input_likelihoods"][key]
        for key, prior in result["input_priors"].items()
    }
    expected = weights[hypothesis] / math.fsum(weights.values())
    assert result["mathematical_posteriors"][hypothesis] == pytest.approx(expected)


def test_demo_highest_hypothesis_is_just_a_math_rank(ui_app):
    _, app = ui_app
    result = app.calculate_illustrative_bayesian_demo()
    best = max(result["mathematical_posteriors"], key=result["mathematical_posteriors"].get)
    assert result["highest_posterior_hypothesis"] == best
    assert result["discovery_status"] == "NOT_DEMONSTRATED"


def test_demo_repeat_is_deterministic_without_new_evidence(ui_app):
    _, app = ui_app
    assert app.calculate_illustrative_bayesian_demo() == app.calculate_illustrative_bayesian_demo()


def test_demo_output_is_json_serializable_without_nan(ui_app):
    _, app = ui_app
    report = app.calculate_illustrative_bayesian_demo()
    assert json.loads(json.dumps(report, allow_nan=False)) == report


def test_demo_does_not_execute_orchestrator(ui_app, monkeypatch):
    _, app = ui_app
    records = _install_orchestrator(monkeypatch, app)
    app.calculate_illustrative_bayesian_demo()
    assert records == []


def test_demo_does_not_modify_illustrative_input_table(ui_app):
    _, app = ui_app
    before = dict(app.ILLUSTRATIVE_LIKELIHOODS)
    app.calculate_illustrative_bayesian_demo()
    assert app.ILLUSTRATIVE_LIKELIHOODS == before


def test_demo_mutating_returned_inputs_does_not_change_next_run(ui_app):
    _, app = ui_app
    before = app.calculate_illustrative_bayesian_demo()
    before["input_likelihoods"]["H1_Olivine_Pnma"] = 0
    after = app.calculate_illustrative_bayesian_demo()
    assert after["input_likelihoods"]["H1_Olivine_Pnma"] > 0


def test_cif_parser_roundtrip_real_pymatgen(ui_app, cif_bytes):
    _, app = ui_app
    structure = app.parse_user_cif(cif_bytes)
    assert isinstance(structure, Structure)
    assert len(structure) == 2


def test_cif_parser_preserves_composition(ui_app, cif_bytes):
    _, app = ui_app
    structure = app.parse_user_cif(cif_bytes)
    assert structure.composition.get_atomic_fraction("Li") == pytest.approx(0.5)
    assert structure.composition.get_atomic_fraction("O") == pytest.approx(0.5)


def test_cif_parser_supports_utf8_sig(ui_app, cif_bytes):
    _, app = ui_app
    structure = app.parse_user_cif(b"\xef\xbb\xbf" + cif_bytes)
    assert len(structure) == 2


@pytest.mark.parametrize("bad", [None, b"", "", "cif", 23, [], {}, bytearray(b"x")])
def test_cif_parser_rejects_missing_or_non_bytes(ui_app, bad):
    _, app = ui_app
    with pytest.raises(ValueError, match="nonempty CIF"):
        app.parse_user_cif(bad)


@pytest.mark.parametrize("bad", [
    b"\xff", b"\xfe", b"\xff\xfe", b"\x80cif", b"\xc3\x28",
])
def test_cif_parser_rejects_undecodable_content(ui_app, bad):
    _, app = ui_app
    with pytest.raises(ValueError, match="UTF-8"):
        app.parse_user_cif(bad)


@pytest.mark.parametrize("bad", [b"garbage", b"xyz", b"no lattice data", b"99999"])
def test_cif_parser_rejects_invalid_crystal_data(ui_app, bad):
    _, app = ui_app
    with pytest.raises(ValueError, match="Could not parse"):
        app.parse_user_cif(bad)


def test_cif_parser_rejects_oversized_bytes_before_decoding(ui_app):
    _, app = ui_app
    with pytest.raises(ValueError, match="too large"):
        app.parse_user_cif(b"x" * (app.MAX_CIF_BYTES + 1))


def test_cif_parser_accepts_maximum_input_size_check_without_model(ui_app, monkeypatch):
    _, app = ui_app
    calls = []

    class FakeStructure:
        def __len__(self):
            return 1

        @classmethod
        def from_str(cls, text, fmt):
            calls.append((len(text), fmt))
            return cls()

    monkeypatch.setattr(app, "Structure", FakeStructure)
    result = app.parse_user_cif(b"x" * app.MAX_CIF_BYTES)
    assert isinstance(result, FakeStructure)
    assert calls == [(app.MAX_CIF_BYTES, "cif")]


@pytest.mark.parametrize("size", [0, 201, 1000])
def test_cif_parser_rejects_disallowed_site_count(ui_app, monkeypatch, size):
    _, app = ui_app

    class FakeStructure:
        @classmethod
        def from_str(cls, text, fmt):
            return cls()

        def __len__(self):
            return size

    monkeypatch.setattr(app, "Structure", FakeStructure)
    with pytest.raises(ValueError, match="1–200"):
        app.parse_user_cif(b"synthetic for parser boundary testing")


@pytest.mark.parametrize("bad", [None, "LiO", 1, {}, [], False, True])
def test_candidate_metadata_rejects_non_structure(ui_app, bad):
    _, app = ui_app
    with pytest.raises(ValueError, match="valid candidate"):
        app.candidate_metadata(bad)


def test_candidate_metadata_discloses_unverified_provenance(ui_app, cif_bytes):
    _, app = ui_app
    structure = app.parse_user_cif(cif_bytes)
    metadata = app.candidate_metadata(structure)
    assert metadata["input_provenance"] == "USER_SUPPLIED_CIF_NOT_EXPERIMENTALLY_VERIFIED"
    assert metadata["physical_stability_status"] == "NOT_EVALUATED"


def test_candidate_metadata_reports_exact_site_count(ui_app, cif_bytes):
    _, app = ui_app
    structure = app.parse_user_cif(cif_bytes)
    assert app.candidate_metadata(structure)["site_count"] == len(structure)


@pytest.mark.parametrize("key,dimension", [
    ("lattice_a_angstrom", "a"), ("lattice_b_angstrom", "b"),
    ("lattice_c_angstrom", "c")
])
def test_candidate_metadata_records_only_input_lattice(ui_app, cif_bytes, key, dimension):
    _, app = ui_app
    structure = app.parse_user_cif(cif_bytes)
    assert app.candidate_metadata(structure)[key] == pytest.approx(
        float(getattr(structure.lattice, dimension))
    )


def test_candidate_metadata_never_contains_energy_bandgap_or_stability_score(ui_app, cif_bytes):
    _, app = ui_app
    metadata = app.candidate_metadata(app.parse_user_cif(cif_bytes))
    for forbidden in ("e_form", "band_gap_eV", "energy_above_hull", "is_stable",
                      "synthesizability_score", "novelty_score"):
        assert forbidden not in metadata


def test_positions_table_reports_only_supplied_coordinates(ui_app, cif_bytes):
    ui, app = ui_app
    structure = app.parse_user_cif(cif_bytes)
    app._show_positions(structure)
    rows = ui.calls("dataframe")[0][0][0]
    assert len(rows) == len(structure)
    assert set(rows[0]) == {"species", "x_fractional", "y_fractional", "z_fractional"}


def test_positions_caption_denies_validation_claim(ui_app, cif_bytes):
    ui, app = ui_app
    app._show_positions(app.parse_user_cif(cif_bytes))
    assert "not an optimized" in ui.calls("caption")[0][0][0]


def test_demo_page_displays_provenance_download(ui_app):
    ui, app = ui_app
    app._render_demonstration()
    downloads = ui.calls("download_button")
    assert len(downloads) == 1
    args, kwargs = downloads[0]
    report = json.loads(kwargs["data"])
    assert report["model_execution_status"] == "NOT_RUN"
    assert report["discovery_status"] == "NOT_DEMONSTRATED"
    assert kwargs["mime"] == "application/json"


def test_demo_page_never_calls_mlff(ui_app, monkeypatch):
    ui, app = ui_app
    records = _install_orchestrator(monkeypatch, app)
    app._render_demonstration()
    assert records == []


def test_demo_page_shows_three_hypotheses(ui_app):
    ui, app = ui_app
    app._render_demonstration()
    rows = ui.calls("dataframe")[0][0][0]
    assert len(rows) == 3
    assert all("Posterior (mathematical result)" in row for row in rows)


def test_optional_chgnet_page_without_file_does_not_instantiate_model(ui_app, monkeypatch):
    ui, app = ui_app
    records = _install_orchestrator(monkeypatch, app)
    app._render_optional_chgnet()
    assert records == []
    assert len(ui.calls("button")) == 0


def test_optional_page_file_uploader_accepts_only_cif(ui_app):
    ui, app = ui_app
    app._render_optional_chgnet()
    assert ui.calls("file_uploader")[0][1]["type"] == ["cif"]


def test_optional_chgnet_bad_input_does_not_instantiate_model(ui_app, monkeypatch):
    ui, app = ui_app
    records = _install_orchestrator(monkeypatch, app)
    _run_uploaded(ui, app, b"NOT A CIF", consent=True, press=True)
    assert records == []
    assert ui.calls("error")


def test_optional_chgnet_without_consent_is_disabled(ui_app, monkeypatch, cif_bytes):
    ui, app = ui_app
    records = _install_orchestrator(monkeypatch, app)
    _run_uploaded(ui, app, cif_bytes, consent=False, press=True)
    assert records == []
    assert ui.calls("button")[0][1]["disabled"] is True


def test_optional_chgnet_with_consent_but_no_button_press_does_not_execute(
    ui_app, monkeypatch, cif_bytes
):
    ui, app = ui_app
    records = _install_orchestrator(monkeypatch, app)
    _run_uploaded(ui, app, cif_bytes, consent=True, press=False)
    assert records == []
    assert ui.calls("button")[0][1]["disabled"] is False


def test_optional_chgnet_explicitly_authorized_run_executes_once(
    ui_app, monkeypatch, cif_bytes
):
    ui, app = ui_app
    records = _install_orchestrator(monkeypatch, app)
    _run_uploaded(ui, app, cif_bytes, consent=True, press=True)
    assert len(records) == 2
    assert records[0] == ("init", {"max_iterations": 1, "use_mlff": True})
    assert records[1][0] == "run"
    assert isinstance(records[1][2], Structure)


def test_optional_chgnet_receives_matching_formula(
    ui_app, monkeypatch, cif_bytes
):
    ui, app = ui_app
    records = _install_orchestrator(monkeypatch, app)
    _run_uploaded(ui, app, cif_bytes, consent=True, press=True)
    assert records[1][1] == records[1][2].composition.reduced_formula


def test_optional_run_records_uploaded_cif_sha256(ui_app, monkeypatch, cif_bytes):
    ui, app = ui_app
    _install_orchestrator(monkeypatch, app)
    _run_uploaded(ui, app, cif_bytes, consent=True, press=True)
    assert ui.session_state["bhs_optional_chgnet_cif_hash"] == hashlib.sha256(
        cif_bytes
    ).hexdigest()


def test_optional_run_records_model_execution_status(ui_app, monkeypatch, cif_bytes):
    ui, app = ui_app
    _install_orchestrator(monkeypatch, app)
    _run_uploaded(ui, app, cif_bytes, consent=True, press=True)
    assert ui.session_state["bhs_optional_chgnet_result"].execution_status == (
        "CHGNET_OPTIMIZER_RETURNED_OUTPUT"
    )


def test_optional_run_displays_only_model_potential_energy(ui_app, monkeypatch, cif_bytes):
    ui, app = ui_app
    _install_orchestrator(monkeypatch, app)
    _run_uploaded(ui, app, cif_bytes, consent=True, press=True)
    metrics = ui.calls("metric")
    assert len(metrics) == 1
    assert "potential energy" in metrics[0][0][0]
    assert "-3.250000" in metrics[0][0][1]
    assert not any("formation energy" in metric[0][0].lower() for metric in metrics)


def test_optional_run_reports_stability_not_verified(ui_app, monkeypatch, cif_bytes):
    ui, app = ui_app
    _install_orchestrator(monkeypatch, app)
    _run_uploaded(ui, app, cif_bytes, consent=True, press=True)
    assert any("NOT_EVALUATED" in str(args) for args, _ in ui.calls("write"))


def test_optional_run_does_not_claim_verified_convergence(ui_app, monkeypatch, cif_bytes):
    ui, app = ui_app
    _install_orchestrator(monkeypatch, app)
    _run_uploaded(ui, app, cif_bytes, consent=True, press=True)
    assert any("NOT_VERIFIED" in str(args) for args, _ in ui.calls("write"))


def test_optional_run_primary_failure_returns_no_energy_metric(ui_app, monkeypatch, cif_bytes):
    ui, app = ui_app
    _install_orchestrator(monkeypatch, app, result=_model_result(state="FAILED"))
    _run_uploaded(ui, app, cif_bytes, consent=True, press=True)
    assert ui.calls("metric") == []
    assert any("No physical result" in str(args) for args, _ in ui.calls("error"))


@pytest.mark.parametrize("error", [
    ImportError("CHGNet missing"),
    OSError("weights missing"),
    ValueError("invalid primary output"),
    RuntimeError("device failure"),
])
def test_optional_run_exceptions_are_reported_and_not_fabricated(
    ui_app, monkeypatch, cif_bytes, error
):
    ui, app = ui_app
    _install_orchestrator(monkeypatch, app, failure=error)
    _run_uploaded(ui, app, cif_bytes, consent=True, press=True)
    assert ui.calls("metric") == []
    assert any("Evaluation aborted" in str(args) for args, _ in ui.calls("error"))
    assert "bhs_optional_chgnet_result" not in ui.session_state


def test_optional_run_no_metric_when_model_energy_missing(ui_app, monkeypatch, cif_bytes):
    ui, app = ui_app
    _install_orchestrator(monkeypatch, app, result=_model_result(energy=None))
    _run_uploaded(ui, app, cif_bytes, consent=True, press=True)
    assert ui.calls("metric") == []


def test_optional_page_does_not_display_stale_cif_result(
    ui_app, monkeypatch, cif_bytes
):
    ui, app = ui_app
    _install_orchestrator(monkeypatch, app)
    _run_uploaded(ui, app, cif_bytes, consent=True, press=True)
    assert len(ui.calls("metric")) == 1
    ui.events.clear()
    ui.press = False
    different = b"\xef\xbb\xbf" + cif_bytes
    _run_uploaded(ui, app, different, consent=True, press=False)
    assert ui.calls("metric") == []


def test_optional_page_reuses_same_cif_prior_result_without_rerunning(
    ui_app, monkeypatch, cif_bytes
):
    ui, app = ui_app
    records = _install_orchestrator(monkeypatch, app)
    _run_uploaded(ui, app, cif_bytes, consent=True, press=True)
    ui.events.clear()
    _run_uploaded(ui, app, cif_bytes, consent=False, press=False)
    assert len(records) == 2
    assert len(ui.calls("metric")) == 1


def test_provenance_table_explicitly_rejects_material_discovery(ui_app):
    ui, app = ui_app
    app._render_provenance()
    rows = ui.calls("table")[0][0][0]
    assert any(
        row["Capability"] == "Novel materials discovery"
        and row["Status"] == "NOT_DEMONSTRATED"
        for row in rows
    )


@pytest.mark.parametrize("capability,expected", [
    ("MCTS/PUCT rollouts", "NOT_RUN"),
    ("Formation energy / convex-hull stability", "NOT_CALCULATED"),
    ("Independent MACE/M3GNet or DFT consensus", "NOT_RUN"),
    ("Calibrated experimental/physical likelihoods", "NOT_VERIFIED"),
    ("CHGNet", "OPTIONAL — USER INITIATED ONLY"),
])
def test_provenance_table_has_explicit_capability_status(ui_app, capability, expected):
    ui, app = ui_app
    app._render_provenance()
    rows = ui.calls("table")[0][0][0]
    assert any(row["Capability"] == capability and row["Status"] == expected for row in rows)


def test_main_sets_page_title_and_three_tabs(ui_app):
    ui, app = ui_app
    app.main()
    assert ui.calls("set_page_config")[0][1]["page_title"] == "BHS Research Prototype"
    assert len(ui.calls("tabs")[0][0][0]) == 3


def test_main_defaults_to_no_model_execution(ui_app, monkeypatch):
    ui, app = ui_app
    records = _install_orchestrator(monkeypatch, app)
    app.main()
    assert records == []
    assert ui.calls("warning")


def test_main_never_shows_bandgap_or_formation_energy_metric(ui_app):
    ui, app = ui_app
    app.main()
    assert ui.calls("metric") == []
    assert ui.calls("download_button")


# END OF COMPLETE BHS STREAMLIT APP SAFETY TESTS — CHECK THIS LINE ON GITHUB
