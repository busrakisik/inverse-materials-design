# BEGIN OF COMPLETE BHS SCIENTIFICALLY HONEST STREAMLIT APP — CHECK THIS LINE ON GITHUB
"""BHS research prototype UI: a labelled Bayesian demo and optional CHGNet.

Nothing executes a physics model on page load. Illustrative likelihoods are
not observations, calibrated probabilities or physical evidence. The optional
CHGNet path requires an explicitly uploaded CIF and user authorization.
No DFT, experimental validation, MCTS, formation energy, band gap, material
novelty or thermodynamic stability is calculated or claimed here.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

import streamlit as st
from pymatgen.core import Structure

from bhs.cli import ILLUSTRATIVE_LIKELIHOODS
from bhs.search.bayesian_engine import BayesianHypothesisSearchEngine
from src.imd_pipeline.pipeline.orchestrator import Orchestrator

MAX_CIF_BYTES = 2_000_000
MAX_SITES = 200
DEMO_STATUS = "ILLUSTRATIVE_DEMO_NOT_PHYSICAL_EVIDENCE"


def calculate_illustrative_bayesian_demo() -> Dict[str, Any]:
    """Use the audited mathematical updater with explicitly artificial inputs."""
    engine = BayesianHypothesisSearchEngine()
    original_priors = dict(engine.priors)
    report = engine.accumulate_evidence(
        "ILLUSTRATIVE likelihood update — no scientific observation",
        dict(ILLUSTRATIVE_LIKELIHOODS),
    )
    posterior = {
        name: float(item.value) for name, item in report["posteriors"].items()
    }
    return {
        "mode": DEMO_STATUS,
        "input_prior_provenance": "HARDCODED_ILLUSTRATIVE_VALUES",
        "input_likelihood_provenance": "HARDCODED_ILLUSTRATIVE_VALUES",
        "input_priors": original_priors,
        "input_likelihoods": dict(ILLUSTRATIVE_LIKELIHOODS),
        "mathematical_posteriors": posterior,
        "highest_posterior_hypothesis": report["winning_hypothesis"],
        "physical_evidence_status": "NOT_VERIFIED",
        "model_execution_status": "NOT_RUN",
        "bayesian_likelihood_calibration_status": "NOT_VERIFIED",
        "mcts_rollouts_executed": False,
        "gpu_hours_allocated": None,
        "formation_energy_ev_per_atom": None,
        "band_gap_eV": None,
        "stability_status": "NOT_EVALUATED",
        "discovery_status": "NOT_DEMONSTRATED",
    }


def parse_user_cif(data: bytes) -> Structure:
    """Parse only a deliberately supplied, size-capped CIF structure."""
    if not isinstance(data, bytes) or not data:
        raise ValueError("Please upload a nonempty CIF file.")
    if len(data) > MAX_CIF_BYTES:
        raise ValueError("CIF file is too large (maximum 2 MB).")
    try:
        cif_text = data.decode("utf-8-sig")
    except UnicodeError as exc:
        raise ValueError("CIF content must be UTF-8 encoded.") from exc
    try:
        structure = Structure.from_str(cif_text, fmt="cif")
    except Exception as exc:
        raise ValueError("Could not parse the supplied CIF structure.") from exc
    if not isinstance(structure, Structure) or not 0 < len(structure) <= MAX_SITES:
        raise ValueError("CIF must contain 1–200 crystallographic sites.")
    return structure


def candidate_metadata(structure: Structure) -> Dict[str, Any]:
    """Describe a parsed input without making a physics/stability claim."""
    if not isinstance(structure, Structure) or not 0 < len(structure) <= MAX_SITES:
        raise ValueError("A valid candidate structure is required.")
    return {
        "input_provenance": "USER_SUPPLIED_CIF_NOT_EXPERIMENTALLY_VERIFIED",
        "formula": str(structure.composition.reduced_formula),
        "site_count": len(structure),
        "lattice_a_angstrom": float(structure.lattice.a),
        "lattice_b_angstrom": float(structure.lattice.b),
        "lattice_c_angstrom": float(structure.lattice.c),
        "physical_stability_status": "NOT_EVALUATED",
    }


def _show_positions(structure: Structure) -> None:
    rows = []
    for site in structure:
        frac = site.frac_coords
        rows.append({
            "species": str(site.species),
            "x_fractional": float(frac[0]),
            "y_fractional": float(frac[1]),
            "z_fractional": float(frac[2]),
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.caption(
        "These are positions parsed from the supplied CIF, not an optimized "
        "or experimentally validated crystal. Bonding and stability are not inferred."
    )


def _render_demonstration() -> None:
    st.subheader("Illustrative Bayesian probability update")
    st.info(
        "This is a mathematical demonstration, NOT a materials experiment. "
        "The priors and likelihoods are manually specified examples."
    )
    demo = calculate_illustrative_bayesian_demo()
    rows = []
    for name, prior in demo["input_priors"].items():
        rows.append({
            "Hypothesis (illustrative label)": name,
            "Prior (illustrative)": round(prior, 6),
            "Likelihood (illustrative)": round(demo["input_likelihoods"][name], 6),
            "Posterior (mathematical result)": round(
                demo["mathematical_posteriors"][name], 6
            ),
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.latex(
        r"P(H_i\mid E)=\frac{P(E\mid H_i)P(H_i)}{\sum_j P(E\mid H_j)P(H_j)}"
    )
    st.caption(
        "The highest illustrative posterior is not a discovered structure, "
        "validated scientific hypothesis, or demonstrated physical advantage. "
        "No tree-search rollouts, DFT, MLFF, GPU allocation, or experiments ran."
    )
    st.download_button(
        "Download illustrative probabilities + provenance (JSON)",
        data=json.dumps(demo, indent=2, ensure_ascii=False),
        file_name="bhs_illustrative_bayesian_demo.json",
        mime="application/json",
    )


def _render_optional_chgnet() -> None:
    st.subheader("Optional single-candidate CHGNet prediction")
    st.warning(
        "Requires a caller-supplied CIF and a separately installed, compatible "
        "CHGNet package. The first explicit run may load or download model weights. "
        "Predicted potential energy is NOT formation energy or a stability proof."
    )
    uploaded = st.file_uploader(
        "Upload a CIF crystal file", type=["cif"], key="bhs_uploaded_cif"
    )
    if uploaded is None:
        st.info("No CIF supplied; no structure generation or MLFF execution occurs.")
        return
    data = uploaded.getvalue()
    try:
        structure = parse_user_cif(data)
    except ValueError as exc:
        st.error(f"Input error: {exc}")
        return

    fingerprint = hashlib.sha256(data).hexdigest()
    meta = candidate_metadata(structure)
    st.json(meta)
    with st.expander("Inspect the uploaded fractional coordinates"):
        _show_positions(structure)

    consent = st.checkbox(
        "I understand that CHGNet is optional and returns unverified model "
        "predictions, not experimental evidence or a stability certificate.",
        value=False,
    )
    run = st.button(
        "Run CHGNet for this uploaded candidate",
        type="primary",
        disabled=not consent,
    )
    if run:
        # This is the only route in the app that can invoke CHGNet.
        try:
            with st.spinner("Running explicit CHGNet evaluation..."):
                result = Orchestrator(max_iterations=1, use_mlff=True).run_discovery_loop(
                    target_formula=str(structure.composition.reduced_formula),
                    initial_structure=structure,
                )
        except Exception as exc:
            st.error(f"Evaluation aborted: {type(exc).__name__}: {exc}")
            return
        st.session_state["bhs_optional_chgnet_result"] = result
        st.session_state["bhs_optional_chgnet_cif_hash"] = fingerprint

    result = st.session_state.get("bhs_optional_chgnet_result")
    if result is None or st.session_state.get("bhs_optional_chgnet_cif_hash") != fingerprint:
        return

    st.write("**Reported execution status:**", result.execution_status)
    st.write("**Stability:**", result.stability_status)
    st.write("**Independent convergence verification:**", result.convergence_status)
    st.caption(result.scientific_interpretation)
    if result.execution_status == "FAILED":
        st.error("CHGNet failed. No physical result was substituted.")
    elif result.execution_status == "CHGNET_OPTIMIZER_RETURNED_OUTPUT":
        record = result.history[0]
        energy = record.get("potential_energy_ev_per_atom")
        if energy is not None:
            st.metric("CHGNet-predicted potential energy (eV/atom)", f"{energy:.6f}")
        st.caption(
            "Model-predicted potential energy only. No formation energy, "
            "band gap, energy above hull, synthesis score, or independent "
            "stability verification is available."
        )
    else:
        st.info("No model result was obtained.")


def _render_provenance() -> None:
    st.subheader("Implemented versus unverified capabilities")
    st.table([
        {"Capability": "Bayesian arithmetic on example inputs", "Status": "IMPLEMENTED — DEMO ONLY"},
        {"Capability": "Calibrated experimental/physical likelihoods", "Status": "NOT_VERIFIED"},
        {"Capability": "Autonomous crystal generator and iterative feedback", "Status": "NOT_IMPLEMENTED HERE"},
        {"Capability": "MCTS/PUCT rollouts", "Status": "NOT_RUN"},
        {"Capability": "CHGNet", "Status": "OPTIONAL — USER INITIATED ONLY"},
        {"Capability": "Independent MACE/M3GNet or DFT consensus", "Status": "NOT_RUN"},
        {"Capability": "Formation energy / convex-hull stability", "Status": "NOT_CALCULATED"},
        {"Capability": "Band gap / synthesis probability / patent clearance", "Status": "NOT_EVALUATED"},
        {"Capability": "Novel materials discovery", "Status": "NOT_DEMONSTRATED"},
    ])
    st.caption(
        "Passing software tests demonstrates scoped implementation behavior, "
        "not experimental accuracy, reliable material screening, or novelty."
    )


def main() -> None:
    st.set_page_config(page_title="BHS Research Prototype", page_icon="🧪", layout="wide")
    st.title("Bayesian Hypothesis Search · Research Prototype")
    st.warning(
        "SCIENTIFIC STATUS: Software prototype only. Illustrative inputs are "
        "not physical evidence; predictions are not experimental validation."
    )
    demo, chgnet, provenance = st.tabs([
        "Illustrative Bayes update", "Optional CHGNet (CIF)", "Provenance & limits"
    ])
    with demo:
        _render_demonstration()
    with chgnet:
        _render_optional_chgnet()
    with provenance:
        _render_provenance()


if __name__ == "__main__":
    main()

# END OF COMPLETE BHS SCIENTIFICALLY HONEST STREAMLIT APP — CHECK THIS LINE ON GITHUB
