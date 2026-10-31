# BEGIN OF COMPLETE BHS CLI FILE — CHECK THIS LINE ON GITHUB
"""BHS command-line entry point for a transparent Bayesian-update demonstration.

This CLI deliberately performs NO crystal-structure validation, CHGNet
relaxation, GPU computation, or autonomous material discovery.

The illustrative likelihoods are examples, not scientifically calibrated
evidence. Actual materials-workflow execution requires a separate,
validated pipeline with physical inputs and reproducibility checks.
"""

import argparse
from pathlib import Path
import math

import yaml

from bhs.search.bayesian_engine import BayesianHypothesisSearchEngine
from bhs.provenance.bundle import ProvenanceBundleSaver


# These are illustrative numbers reused from the old demonstration code.
# They are NOT physical likelihoods obtained from experiments or MLFF.
ILLUSTRATIVE_LIKELIHOODS = {
    "H1_Olivine_Pnma": 0.95,
    "H2_Spinel_Fd3m": 0.32,
    "H3_NASICON_R3c": 0.15,
}


def _validate_priors(priors):
    if not isinstance(priors, dict) or not priors:
        raise ValueError("Config must provide a nonempty 'priors' mapping.")
    if set(priors) != set(ILLUSTRATIVE_LIKELIHOODS):
        raise ValueError(
            "The demonstration supports exactly H1_Olivine_Pnma, "
            "H2_Spinel_Fd3m and H3_NASICON_R3c. "
            "It does not silently invent likelihoods for other hypotheses."
        )
    for name, probability in priors.items():
        if (
            isinstance(probability, bool)
            or not isinstance(probability, (int, float))
            or not math.isfinite(probability)
            or probability <= 0
        ):
            raise ValueError(f"Invalid prior probability for {name!r}.")
    if not math.isclose(sum(priors.values()), 1.0, rel_tol=0, abs_tol=1e-7):
        raise ValueError("Priors must sum to 1.0.")


def run_pipeline(config_path: str, out_dir: str, *, demo: bool = False) -> str:
    """Save a NOT_VERIFIED Bayesian demo bundle; never claim a material result."""
    if not demo:
        raise ValueError(
            "A validated physical discovery pipeline is not implemented. "
            "Run with --demo for illustrative Bayesian calculations only."
        )

    with Path(config_path).open("r", encoding="utf-8") as file:
        source_config = yaml.safe_load(file)
    if not isinstance(source_config, dict):
        raise ValueError("YAML configuration must be a mapping.")
    priors = source_config.get("priors")
    _validate_priors(priors)

    engine = BayesianHypothesisSearchEngine(initial_priors=dict(priors))
    record = engine.accumulate_evidence(
        step_name="ILLUSTRATIVE evidence update — no physical measurement",
        likelihoods=dict(ILLUSTRATIVE_LIKELIHOODS),
    )
    # Do not store the engine's illustrative GPU-hour budget as an allocation.
    posterior_probabilities = {
        name: float(value.value) for name, value in record["posteriors"].items()
    }

    config_record = {
        "experiment_name": "BHS_ILLUSTRATIVE_BAYES_DEMO",
        "mode": "ILLUSTRATIVE_DEMO_NOT_VERIFIED",
        "target_composition": source_config.get("target_composition", "not specified"),
        "source_configuration": source_config,
        "likelihood_source": "HARDCODED_ILLUSTRATIVE_VALUES",
        "physical_constraints_applied": False,
        "MLFF_executed": False,
        "search_budget_allocated": False,
    }
    history = [
        {
            "step_name": "ILLUSTRATIVE Bayesian evidence update",
            "input_priors": dict(priors),
            "input_likelihoods": dict(ILLUSTRATIVE_LIKELIHOODS),
            "evidence_provenance": "ILLUSTRATIVE",
            "posteriors": posterior_probabilities,
            "highest_posterior_hypothesis": record["winning_hypothesis"],
            "physical_validation": "NOT_RUN",
            "gpu_hours_allocated": None,
     }
    ]
    metrics = {
        "status": "DEMO_ONLY_NOT_VERIFIED",
        "evidence_provenance": "ILLUSTRATIVE",
        "posteriors_from_illustrative_inputs": posterior_probabilities,
        "physical_relaxation": "NOT_RUN",
        "energy_ev_per_atom": None,
        "GPU_hours_measured": None,
        "materials_discovered": None,
    }
    saved = ProvenanceBundleSaver.create_run_bundle(
        out_dir=out_dir,
        config=config_record,
        run_history=history,
        final_metrics=metrics,
    )
    print(
        "ILLUSTRATIVE DEMO completed. No physical experiment or materials "
        f"discovery was performed. NOT_VERIFIED records saved to: {Path(saved).resolve()}"
    )
    return saved


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="BHS illustrative Bayesian-update demo; not a validated materials workflow."
    )
    parser.add_argument("--config", required=True, help="YAML configuration with priors")
    parser.add_argument("--out-dir", default="./runs/demo_001", help="Output directory")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Explicitly permit illustrative likelihood updates with no physics run",
    )
    args = parser.parse_args(argv)
    try:
        run_pipeline(args.config, args.out_dir, demo=args.demo)
    except (ValueError, FileNotFoundError, yaml.YAMLError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")


if __name__ == "__main__":
    main()

# END OF COMPLETE BHS CLI FILE — CHECK THIS LINE ON GITHUB
