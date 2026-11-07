"""V12.5: group-disjoint calibration of selective research decisions.

Manufactured development evidence only. Calibration is serialized in a first
stage; only the second stage constructs evaluation groups. Policies receive
public descriptors and actually revealed responses, never hidden outcomes.
No physical source is retrieved, and no laboratory action is authorized.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from scripts.bhs_measurement_allocation_v12 import (
    INITIAL_MEASUREMENTS, INITIAL_GEOMETRIES, TOTAL_MEASUREMENTS, REPEATS,
    MeasurementContractError, initial_geometry_ids, require_development_seed,
)
from scripts.bhs_v124_completion_coverage_audit import (
    POLICIES, propose_action, _observed_summary, _valid_action,
)

SOURCE_SEED = 12507011
NOISE_SEED = 12507019
POOL_SIZE = 48
CAL_SPECS = (
    (101, "ridge", "constant", 17),
    (103, "oscillatory", "varying", 37),
    (107, "ridge", "batch", 41),
    (109, "oscillatory", "constant", 53),
)
EVAL_SPECS = (
    (211, "ridge", "constant", 17),
    (223, "oscillatory", "varying", 37),
    (227, "ridge", "batch", 41),
    (229, "shifted", "batch", 53),
)
ORDER_VARIANTS = (0, 1)
COVERAGE_CAPS = (0.25, 0.50, 0.75)
PRIMARY_COVERAGE = 0.50
ERROR_CAP = 0.25
REGRET_TOLERANCE = 0.35
ABSTENTION_COST = 0.50
PROTOCOL_GIT_BLOB = "719431338ee9cd0b3ecc50d197b946aeb79c4701"
HARD_GATES = {
    "development_only": True,
    "scored_validation_allowed": False,
    "independent_holdout_used": False,
    "physical_validation_by_bhs": False,
    "causal_identification": False,
    "calibrated_uncertainty_proven": False,
    "claim_of_superiority": False,
    "real_savings_measured": False,
    "reserved_nist_seeds_used": False,
}


@dataclass(frozen=True)
class GroupSource:
    descriptors: np.ndarray
    latent: np.ndarray
    outcomes: np.ndarray
    group: int
    landscape: str
    noise: str
    fingerprint: str


def spec_for(split: str):
    if split == "calibration":
        return CAL_SPECS
    if split == "evaluation":
        return EVAL_SPECS
    raise MeasurementContractError("UNRECOGNIZED_SPLIT")


def make_group_source(spec, *, split: str) -> GroupSource:
    if spec not in spec_for(split):
        raise MeasurementContractError("GROUP_NOT_ASSIGNED_TO_SPLIT")
    group, landscape, noise_kind, seed = spec
    require_development_seed(seed)
    x = np.random.default_rng(
        np.random.SeedSequence([SOURCE_SEED, group, 1])
    ).uniform(-1.0, 1.0, (POOL_SIZE, 4))
    if landscape == "ridge":
        latent = (3.0 + 1.4 * np.exp(-6.0 * (x[:, 0]-.35)**2)
                  + .9*x[:, 1] - .6*x[:, 2]**2 + .5*x[:, 0]*x[:, 3])
    elif landscape == "oscillatory":
        latent = (3.0 + 1.1*np.sin(2.5*np.pi*x[:, 0])*np.cos(1.5*np.pi*x[:, 1])
                  + .7*x[:, 2]*x[:, 3] - .4*x[:, 1]**2)
    elif landscape == "shifted":
        latent = (2.6 + 1.3*np.cos(2*np.pi*x[:, 0]*x[:, 1])
                  - .9*x[:, 2] + .6*x[:, 3]**2)
    else:
        raise MeasurementContractError("UNEXPECTED_LATENT_LANDSCAPE")
    z = np.random.default_rng(
        np.random.SeedSequence([NOISE_SEED, group, 2])
    ).normal(size=(POOL_SIZE, REPEATS))
    if noise_kind == "constant":
        noise = .35 * z
    elif noise_kind == "varying":
        sigma = .15+.55*(x[:, 0]+1)/2
        noise = sigma[:, None]*z
    elif noise_kind == "batch":
        batch = np.random.default_rng(
            np.random.SeedSequence([NOISE_SEED, group, 3])
        ).normal(size=POOL_SIZE//8)
        noise = .30*z + (.55*batch[np.arange(POOL_SIZE)//8])[:, None]
    else:
        raise MeasurementContractError("UNEXPECTED_NOISE_PROCESS")
    outcomes = latent[:, None]+noise
    if (x.shape != (POOL_SIZE,4) or latent.shape != (POOL_SIZE,)
            or outcomes.shape != (POOL_SIZE,REPEATS)
            or not np.isfinite(outcomes).all()):
        raise MeasurementContractError("INVALID_MANUFACTURED_GROUP")
    digest = hashlib.sha256(b"".join(
        np.ascontiguousarray(a,dtype="<f8").tobytes()
        for a in (x, latent, outcomes)
    )).hexdigest()
    return GroupSource(x, latent, outcomes, group, landscape, noise_kind, digest)


class PrivateGroupOracle:
    """Never passes its source, latent qualities or future responses to a selector."""
    def __init__(self, source: GroupSource, seed: int, variant: int):
        require_development_seed(seed)
        if type(variant) is not int or variant not in ORDER_VARIANTS:
            raise MeasurementContractError("INVALID_GROUP_ORDER_VARIANT")
        self.__latent = np.asarray(source.latent,float).copy()
        self.__hidden = np.asarray(source.outcomes,float).copy()
        if (self.__hidden.shape != (POOL_SIZE,REPEATS)
                or self.__latent.shape != (POOL_SIZE,)
                or not np.isfinite(self.__hidden).all()
                or not np.isfinite(self.__latent).all()):
            raise MeasurementContractError("INVALID_PRIVATE_GROUP")
        self.__permutations = [
            np.random.default_rng(
                np.random.SeedSequence([SOURCE_SEED,source.group,seed,variant,int(i)])
            ).permutation(REPEATS)
            for i in range(POOL_SIZE)
        ]
        self.__reveals = np.zeros(POOL_SIZE,dtype=np.int8)

    def reveal(self, idx: int, ordinal: int) -> float:
        if (type(idx) is not int or type(ordinal) is not int or
                not 0 <= idx < POOL_SIZE or not 1 <= ordinal <= REPEATS):
            raise MeasurementContractError("INVALID_PRIVATE_REVEAL_REQUEST")
        if ordinal != int(self.__reveals[idx])+1:
            raise MeasurementContractError("REVEAL_ALREADY_USED_OR_SKIPPED")
        value=float(self.__hidden[idx,self.__permutations[idx][ordinal-1]])
        self.__reveals[idx]+=1
        return value

    def finish(self, observed: dict[int,tuple[float,...]]):
        if not isinstance(observed,dict):
            raise MeasurementContractError("NOT_A_TRANSCRIPT")
        ids={i for i,n in enumerate(self.__reveals) if n>0}
        if set(observed)!=ids or any(type(i) is not int for i in observed):
            raise MeasurementContractError("TRANSCRIPT_IDS_DIFFER")
        for i,values in observed.items():
            expected=self.__hidden[i,self.__permutations[i][:int(self.__reveals[i])]]
            if (not isinstance(values,tuple) or len(values)!=len(expected) or
                    not np.array_equal(np.asarray(values,float),expected)):
                raise MeasurementContractError("TRANSCRIPT_VALUES_DIFFER")
        if int(np.sum(self.__reveals))!=TOTAL_MEASUREMENTS:
            raise MeasurementContractError("INCORRECT_MEASUREMENT_BUDGET")
        chosen,margin,stderr=_observed_summary(observed)
        complete=[i for i,v in observed.items() if len(v)==REPEATS]
        partial=[i for i,v in observed.items() if len(v)<REPEATS]
        optimum=float(np.max(self.__latent))
        regret=max(0.0,optimum-float(self.__latent[chosen]))
        if not np.isfinite(margin) or not np.isfinite(stderr):
            raise MeasurementContractError("INVALID_EVIDENCE_MARGIN")
        score=float(margin/max(stderr,1e-8))
        if not np.isfinite(score) or score < 0:
            raise MeasurementContractError("NONFINITE_EVIDENCE_SCORE")
        return {
            "evidence_score":score,
            "latent_recommendation_regret":regret,
            "high_regret_error":bool(regret>REGRET_TOLERANCE),
            "completed_designs":len(complete),
            "incomplete_designs":len(partial),
            "stranded_partial_responses":sum(len(observed[i]) for i in partial),
            "measurement_count":int(np.sum(self.__reveals)),
            "latent_outcomes_passed_to_selector":False,
            "future_responses_passed_to_selector":False,
        }


def run_campaign(split: str, spec, policy: str, variant: int):
    if (policy not in POLICIES or spec not in spec_for(split)
            or type(variant) is not int or variant not in ORDER_VARIANTS):
        raise MeasurementContractError("INVALID_GROUP_CAMPAIGN")
    source=make_group_source(spec,split=split)
    group,landscape,noise,seed=spec
    oracle=PrivateGroupOracle(source,seed,variant)
    public_x=np.asarray(source.descriptors,float).copy()
    observed={}
    for i in initial_geometry_ids(POOL_SIZE,seed):
        observed[i]=tuple(oracle.reveal(i,j) for j in range(1,REPEATS+1))
    overrides=0
    for step in range(TOTAL_MEASUREMENTS-INITIAL_MEASUREMENTS):
        acquired={i:tuple(v) for i,v in observed.items()}
        idx,ordinal,override=propose_action(
            policy,public_x.copy(),acquired,seed=seed,step=step
        )
        if not _valid_action(idx,ordinal,observed,POOL_SIZE):
            raise MeasurementContractError("POLICY_ACTION_CONTRACT_FAILED")
        observed[idx]=observed.get(idx,())+(oracle.reveal(idx,ordinal),)
        overrides+=int(override)
    return {
        "split":split,"group":int(group),"landscape":landscape,"noise":noise,
        "seed":int(seed),"order_variant":int(variant),"policy":policy,
        "completion_interventions":overrides,
        "source_fingerprint":source.fingerprint,
        **oracle.finish(observed)
    }


def select_threshold(rows: list[dict], coverage: float):
    """Use ONLY calibration labels and observed evidence scores.

    Conservative empirical rule: maximize n accepted under the fixed cap on
    accepted calibration coverage and high-regret frequency. No guarantee.
    """
    if coverage not in COVERAGE_CAPS or len(rows)!=len(CAL_SPECS)*len(ORDER_VARIANTS):
        raise MeasurementContractError("INVALID_CALIBRATION_COVERAGE_SAMPLE")
    expected={(s[0],v) for s in CAL_SPECS for v in ORDER_VARIANTS}
    if ({(r["group"],r["order_variant"]) for r in rows}!=expected or
            any(r["split"]!="calibration" or
                type(r["high_regret_error"]) is not bool or
                not np.isfinite(r["evidence_score"]) or
                r["evidence_score"]<0 for r in rows)):
        raise MeasurementContractError("CALIBRATION_ONLY_GROUPS_REQUIRED")
    scores=np.asarray([r["evidence_score"] for r in rows],float)
    errors=np.asarray([r["high_regret_error"] for r in rows],bool)
    # Both sentinels are finite; equality is resolved by strict score > cutoff.
    candidates={float(np.max(scores)+1.0),float(np.min(scores)-1.0)}
    candidates.update(map(float,scores))
    feasible=[]
    for threshold in candidates:
        accepted=scores>threshold
        n=int(accepted.sum())
        if n>math.floor(coverage*len(rows)):
            continue
        error_rate=float(np.mean(errors[accepted])) if n else 0.0
        if error_rate <= ERROR_CAP:
            feasible.append((n,threshold))
    if not feasible:
        raise MeasurementContractError("NO_FEASIBLE_CALIBRATION_THRESHOLD")
    n,t=max(feasible,key=lambda item:(item[0],item[1]))
    return {"threshold":float(t),"accepted":int(n),"denominator":len(rows),
            "coverage":float(n/len(rows)),
            "high_regret_rate":(float(np.mean(errors[scores>t])) if n else None),
            "target_coverage_cap":float(coverage),"empirical_failure_cap":ERROR_CAP}


def calibrate_policy_thresholds(rows):
    """Reject evaluation labels or duplicated/omitted calibration groups."""
    expected=len(CAL_SPECS)*len(ORDER_VARIANTS)*len(POLICIES)
    if len(rows)!=expected:
        raise MeasurementContractError("CALIBRATION_ROW_COUNT_CHANGED")
    if ({(r["group"],r["order_variant"],r["policy"]) for r in rows}
            != {(s[0],v,p) for s in CAL_SPECS for v in ORDER_VARIANTS for p in POLICIES}):
        raise MeasurementContractError("CALIBRATION_CAMPAIGNS_NOT_FROZEN")
    for r in rows:
        regret=r.get("latent_recommendation_regret")
        if (type(regret) not in (int,float) or not np.isfinite(regret) or regret<0
                or r.get("high_regret_error") is not bool(regret>REGRET_TOLERANCE)
                or r.get("measurement_count")!=TOTAL_MEASUREMENTS
                or r.get("incomplete_designs",0)<0
                or r.get("stranded_partial_responses",0)<0):
            raise MeasurementContractError("CALIBRATION_DECISION_RECORD_INCONSISTENT")
    return {
        policy:{f"{coverage:.2f}":select_threshold(
            [r for r in rows if r["policy"]==policy],coverage
        ) for coverage in COVERAGE_CAPS}
        for policy in POLICIES
    }


def _stable_digest(value):
    raw=json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def build_calibration():
    """No evaluation group is constructed or scored in this stage."""
    rows=[run_campaign("calibration",spec,policy,variant)
          for spec in CAL_SPECS for variant in ORDER_VARIANTS for policy in POLICIES]
    thresholds=calibrate_policy_thresholds(rows)
    return {
        "study":"BHS v12.5 disjoint manufactured selective-decision calibration",
        "stage":"calibration","protocol_blob":PROTOCOL_GIT_BLOB,
        "calibration_groups":[s[0] for s in CAL_SPECS],
        "untouched_evaluation_groups":[s[0] for s in EVAL_SPECS],
        "policy_names":list(POLICIES),"order_variants":list(ORDER_VARIANTS),
        "calibration_rows":rows,"calibration_rows_digest":_stable_digest(rows),
        "thresholds":thresholds,"hard_gates":dict(HARD_GATES),
    }


def verify_calibration_document(document):
    if (not isinstance(document,dict) or document.get("stage")!="calibration"
            or document.get("protocol_blob")!=PROTOCOL_GIT_BLOB
            or document.get("calibration_groups")!=[s[0] for s in CAL_SPECS]
            or document.get("untouched_evaluation_groups")!=[s[0] for s in EVAL_SPECS]
            or document.get("policy_names")!=list(POLICIES)
            or document.get("order_variants")!=list(ORDER_VARIANTS)
            or document.get("hard_gates")!=HARD_GATES):
        raise MeasurementContractError("CALIBRATION_METADATA_TAMPERED")
    rows=document.get("calibration_rows")
    if (not isinstance(rows,list) or _stable_digest(rows)!=document.get("calibration_rows_digest")):
        raise MeasurementContractError("CALIBRATION_ROWS_TAMPERED")
    recalculated=calibrate_policy_thresholds(rows)
    if document.get("thresholds")!=recalculated:
        raise MeasurementContractError("CALIBRATION_THRESHOLDS_TAMPERED")
    return recalculated


def _metrics(rows,threshold):
    accepted=[r for r in rows if r["evidence_score"]>threshold]
    n=len(rows)
    k=len(accepted)
    return {
        "accepted":k,"denominator":n,"coverage":float(k/n),
        "conditional_mean_latent_regret":(
            float(np.mean([r["latent_recommendation_regret"] for r in accepted]))
            if k else None),
        "worst_accepted_latent_regret":(
            float(max(r["latent_recommendation_regret"] for r in accepted)) if k else None),
        "accepted_high_regret_error_rate":(
            float(np.mean([r["high_regret_error"] for r in accepted])) if k else None),
        "mean_abstention_adjusted_loss":float(np.mean([
            r["latent_recommendation_regret"] if r["evidence_score"]>threshold
            else ABSTENTION_COST for r in rows
        ])),
        "mean_raw_latent_regret":float(np.mean([r["latent_recommendation_regret"] for r in rows])),
        "mean_incomplete_designs":float(np.mean([r["incomplete_designs"] for r in rows])),
        "mean_stranded_responses":float(np.mean([r["stranded_partial_responses"] for r in rows])),
        "mean_completion_interventions":float(np.mean([r["completion_interventions"] for r in rows])),
    }


def build_evaluation(calibration_document, *, calibration_file_sha256):
    """Verify the frozen calibration object before constructing any eval source."""
    thresholds=verify_calibration_document(calibration_document)
    if (not isinstance(calibration_file_sha256,str) or len(calibration_file_sha256)!=64
            or any(c not in "0123456789abcdef" for c in calibration_file_sha256)):
        raise MeasurementContractError("INVALID_FROZEN_CALIBRATION_DIGEST")
    rows=[run_campaign("evaluation",spec,policy,variant)
          for spec in EVAL_SPECS for variant in ORDER_VARIANTS for policy in POLICIES]
    report={}
    for policy in POLICIES:
        policy_eval=[r for r in rows if r["policy"]==policy]
        report[policy]={}
        for cap in COVERAGE_CAPS:
            key=f"{cap:.2f}"
            t=thresholds[policy][key]["threshold"]
            m=_metrics(policy_eval,t)
            m["coverage_gap_evaluation_minus_calibration"]=(
                m["coverage"]-thresholds[policy][key]["coverage"])
            cal_rate=thresholds[policy][key]["high_regret_rate"]
            m["accepted_error_gap_evaluation_minus_calibration"]=(
                m["accepted_high_regret_error_rate"]-cal_rate
                if cal_rate is not None and m["accepted_high_regret_error_rate"] is not None else None)
            report[policy][key]=m
    by_group={}
    for group,landscape,noise,seed in EVAL_SPECS:
        by_group[str(group)]={
            "landscape":landscape,"noise":noise,
            "policies":{p:_metrics([r for r in rows if r["group"]==group and r["policy"]==p],
                                   thresholds[p][f"{PRIMARY_COVERAGE:.2f}"]["threshold"])
                        for p in POLICIES}
        }
    return {
        "study":"BHS v12.5 group-disjoint manufactured evaluation, development only",
        "stage":"evaluation","protocol_blob":PROTOCOL_GIT_BLOB,
        "calibration_file_sha256":calibration_file_sha256,
        "policy_names":list(POLICIES),"evaluation_groups":[s[0] for s in EVAL_SPECS],
        "calibration_groups":[s[0] for s in CAL_SPECS],
        "thresholds_frozen_from_calibration":thresholds,
        "evaluation_rows":rows,"evaluation_rows_digest":_stable_digest(rows),
        "metrics_by_policy_and_coverage":report,
        "metrics_by_group_at_primary_coverage":by_group,
        "primary_coverage_cap":PRIMARY_COVERAGE,
        "regret_tolerance":REGRET_TOLERANCE,
        "abstention_cost":ABSTENTION_COST,
        "physical_measurements_performed":False,
        "historical_source_accessed":False,
        "hard_gates":dict(HARD_GATES),
    }


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage",choices=("calibration","evaluation"))
    parser.add_argument("--frozen",type=Path)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args(argv)
    if args.stage is None:
        print("Protocol-only mode; no manufactured outcomes scored.")
        return 0
    if args.out is None:
        parser.error("--out required for explicit scored stage")
    if args.stage=="calibration":
        if args.frozen is not None:
            parser.error("calibration stage cannot access a frozen evaluation input")
        report=build_calibration()
    else:
        if args.frozen is None:
            parser.error("evaluation requires a frozen calibration file")
        raw=args.frozen.read_bytes()
        document=json.loads(raw.decode("utf-8"))
        report=build_evaluation(document,calibration_file_sha256=hashlib.sha256(raw).hexdigest())
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print("Completed explicit development stage:",args.stage)
    print("Output:",args.out)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
