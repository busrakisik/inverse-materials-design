"""Static, fail-closed NIST scientific hypothesis research specification.

No dataset downloads, no model fitting, no benchmark, no independent holdout.
This checks a *documentation contract*, NOT scientific model validity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

STATUS = "NIST_SCIENTIFIC_HYPOTHESIS_SPECIFICATION_NOT_EVALUATED"
REGISTRY = Path("research/NIST_SCIENTIFIC_HYPOTHESIS_SPEC_V1.json")
MODELS = ("linear", "fe_co_interaction", "localized_response")
REQUIRED_GATES = (
    "source_order_and_composition_units",
    "target_row_alignment_and_missing_value_policy",
    "domain_review_of_competing_response_families",
    "measurement_uncertainty_or_explicit_sensitivity_protocol",
    "source_reuse_terms_and_pilot_permission",
    "frozen_leakage_safe_protocol_and_strong_baselines",
)
FALSE_FLAGS = (
    "models_are_physical_mechanisms", "composition_column_order_authoritatively_verified",
    "composition_units_authoritatively_verified", "target_row_alignment_authoritatively_verified",
    "measurement_error_per_row_verified", "per_experiment_costs_verified",
    "domain_expert_approved", "source_reuse_terms_cleared", "real_data_fit_performed",
    "real_data_benchmark_performed", "independent_holdout_used", "physical_validation",
    "scored_validation_allowed", "superiority_claim_validated", "dataset_ready_for_bhs",
)


def validate_spec(data):
    if type(data) is not dict or data.get("status") != STATUS or data.get("version") != 1:
        raise ValueError("unexpected specification or version")
    if any(data.get(flag) is not False for flag in FALSE_FLAGS):
        raise ValueError("unreviewed claim upgraded without evidence: fail closed")
    if data.get("model_families_are_phenomenological") is not True:
        raise ValueError("phenomenological models must be labelled")
    source = data.get("source")
    if not isinstance(source, dict) or source.get("repository") != "usnistgov/remi" or source.get("commit") != "596b04435fb577175264a70c4434f5539b809510" or source.get("git_blob_sha1") != "e506db115d522d62618042abead7df2695ccf13e" or source.get("expected_samples") != 921:
        raise ValueError("unexpected NIST pinned source")
    if data.get("primary_target") != "Kerr" or data.get("primary_target_units") != "mrad" or data.get("secondary_target") != "Coer" or data.get("secondary_target_units") != "mT":
        raise ValueError("unexpected target specification")
    if data.get("model_families") != list(MODELS):
        raise ValueError("model families changed without review")
    if data.get("unresolved_gates") != list(REQUIRED_GATES):
        raise ValueError("missing or reordered unresolved gates")
    if not isinstance(data.get("research_question"), str) or "physical-mechanism" not in data["research_question"]:
        raise ValueError("research question must distinguish predictive shapes from physical mechanisms")
    if not isinstance(data.get("selection_rationale"), str) or len(data["selection_rationale"]) < 30:
        raise ValueError("rationale required")
    sources = data.get("literature")
    if not isinstance(sources, list) or len(sources) < 2 or not all(isinstance(x, str) and x.startswith("https://") for x in sources):
        raise ValueError("source citations required")
    return {"status": STATUS, "candidate_families": len(MODELS),
            "primary_target": "Kerr", "unresolved_gates": len(REQUIRED_GATES),
            "dataset_ready_for_bhs": False, "real_data_fit_performed": False,
            "independent_holdout_used": False, "physical_validation": False,
            "scored_validation_allowed": False}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--registry", type=Path, default=REGISTRY)
    p.add_argument("--out-dir", type=Path, default=Path("runs/nist_scientific_hypothesis_spec_v1"))
    args = p.parse_args()
    source = args.registry.read_bytes()
    result = validate_spec(json.loads(source))
    result["spec_sha256"] = hashlib.sha256(source).hexdigest()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    (args.out_dir / "spec_contract_report.json").write_bytes(raw)
    (args.out_dir / "spec_contract_report.sha256").write_text(hashlib.sha256(raw).hexdigest()+"  spec_contract_report.json\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
