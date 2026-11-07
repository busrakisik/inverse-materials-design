"""Group disjointness, calibration isolation and strict manufactured evaluator checks."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
import unittest
from dataclasses import replace
from unittest.mock import patch

import numpy as np

from scripts.bhs_measurement_allocation_v12 import MeasurementContractError, initial_geometry_ids
from scripts.bhs_v124_completion_coverage_audit import POLICIES, propose_action
from scripts.bhs_v125_disjoint_calibration import (
    ABSTENTION_COST, CAL_SPECS, COVERAGE_CAPS, ERROR_CAP, EVAL_SPECS,
    HARD_GATES, ORDER_VARIANTS, POOL_SIZE, PRIMARY_COVERAGE, PROTOCOL_GIT_BLOB,
    REGRET_TOLERANCE, SOURCE_SEED, NOISE_SEED, PrivateGroupOracle, _metrics,
    _stable_digest, build_calibration, build_evaluation, calibrate_policy_thresholds,
    main, make_group_source, run_campaign, select_threshold, spec_for,
    verify_calibration_document,
)


def fake_rows():
    rows=[]
    for spec in CAL_SPECS:
        for variant in ORDER_VARIANTS:
            for policy in POLICIES:
                idx=list(x[0] for x in CAL_SPECS).index(spec[0])*2+variant
                rows.append({"split":"calibration", "group":spec[0],
                    "order_variant":variant,"policy":policy,
                    "evidence_score":float([0.,.3,.5,1.,1.2,1.4,2.,3.][idx]),
                    "high_regret_error":bool(idx<2),
                    "latent_recommendation_regret":float(.5 if idx<2 else .1),
                    "incomplete_designs":0,"stranded_partial_responses":0,
                    "completion_interventions":0,"measurement_count":48})
    return rows


def fake_document(rows=None):
    rows=fake_rows() if rows is None else rows
    return {"study":"fixture","stage":"calibration", "protocol_blob":PROTOCOL_GIT_BLOB,
            "calibration_groups":[s[0] for s in CAL_SPECS],
            "untouched_evaluation_groups":[s[0] for s in EVAL_SPECS],
            "policy_names":list(POLICIES), "order_variants":list(ORDER_VARIANTS),
            "calibration_rows":rows,"calibration_rows_digest":_stable_digest(rows),
            "thresholds":calibrate_policy_thresholds(rows),"hard_gates":dict(HARD_GATES)}


class DisjointCalibrationContracts(unittest.TestCase):
    def test_frozen_protocol_groups_and_disjoint_source_streams(self):
        self.assertEqual((SOURCE_SEED,NOISE_SEED,POOL_SIZE),(12507011,12507019,48))
        self.assertEqual(COVERAGE_CAPS,(.25,.50,.75))
        self.assertEqual((PRIMARY_COVERAGE,ERROR_CAP,REGRET_TOLERANCE,ABSTENTION_COST),
                         (.50,.25,.35,.50))
        self.assertEqual(len(CAL_SPECS),len(EVAL_SPECS))
        self.assertTrue({x[0] for x in CAL_SPECS}.isdisjoint({x[0] for x in EVAL_SPECS}))
        sources=[make_group_source(s,split="calibration") for s in CAL_SPECS]
        other=[make_group_source(s,split="evaluation") for s in EVAL_SPECS]
        self.assertEqual(len({s.fingerprint for s in sources+other}),8)
        self.assertTrue(all(s.descriptors.shape==(48,4) for s in sources+other))
        self.assertTrue(all(s.outcomes.shape==(48,3) for s in sources+other))
        self.assertTrue(all(np.isfinite(s.outcomes).all() for s in sources+other))

    def test_evaluation_only_source_rejected_from_calibration(self):
        with self.assertRaises(MeasurementContractError):
            make_group_source(EVAL_SPECS[0],split="calibration")
        with self.assertRaises(MeasurementContractError):
            make_group_source(CAL_SPECS[0],split="evaluation")
        with self.assertRaises(MeasurementContractError):
            spec_for("both")
        with self.assertRaises(MeasurementContractError):
            run_campaign("calibration",EVAL_SPECS[0],POLICIES[0],0)

    def test_source_stable_within_group_and_different_across_groups(self):
        first=make_group_source(CAL_SPECS[0],split="calibration")
        repeated=make_group_source(CAL_SPECS[0],split="calibration")
        distinct=make_group_source(EVAL_SPECS[0],split="evaluation")
        self.assertEqual(first.fingerprint,repeated.fingerprint)
        np.testing.assert_array_equal(first.outcomes,repeated.outcomes)
        self.assertNotEqual(first.fingerprint,distinct.fingerprint)
        self.assertFalse(np.array_equal(first.descriptors,distinct.descriptors))

    def test_shifted_landscape_exists_only_in_evaluation(self):
        self.assertFalse(any(s[1]=="shifted" for s in CAL_SPECS))
        self.assertEqual(sum(s[1]=="shifted" for s in EVAL_SPECS),1)
        src=make_group_source(EVAL_SPECS[-1],split="evaluation")
        self.assertEqual(src.landscape,"shifted")

    def test_batch_noise_contains_shared_design_offsets(self):
        src=make_group_source(CAL_SPECS[2],split="calibration")
        self.assertEqual(src.noise,"batch")
        spread=np.var(src.outcomes-src.latent[:,None],axis=1)
        self.assertTrue(np.isfinite(spread).all())
        self.assertTrue(np.any(spread>0))

    def test_private_oracle_use_once_and_no_skip(self):
        s=make_group_source(CAL_SPECS[0],split="calibration")
        oracle=PrivateGroupOracle(s,CAL_SPECS[0][3],0)
        with self.assertRaisesRegex(MeasurementContractError,"INVALID_PRIVATE_REVEAL_REQUEST"):
            oracle.reveal(True,1)
        with self.assertRaisesRegex(MeasurementContractError,"USED_OR_SKIPPED"):
            oracle.reveal(0,2)
        oracle.reveal(0,1)
        with self.assertRaisesRegex(MeasurementContractError,"USED_OR_SKIPPED"):
            oracle.reveal(0,1)
        oracle.reveal(0,2);oracle.reveal(0,3)
        with self.assertRaises(MeasurementContractError):
            oracle.reveal(0,3)
        with self.assertRaises(MeasurementContractError):
            PrivateGroupOracle(s,10000,0)

    def test_oracle_copies_hidden_source_before_external_mutation(self):
        s=make_group_source(CAL_SPECS[0],split="calibration")
        original=np.sort(s.outcomes[0].copy())
        oracle=PrivateGroupOracle(s,CAL_SPECS[0][3],0)
        s.outcomes[0]=-1e10
        np.testing.assert_array_equal(
            np.sort([oracle.reveal(0,i) for i in (1,2,3)]),original)

    def test_oracle_rejects_forged_transcripts_and_inexact_budget(self):
        s=make_group_source(CAL_SPECS[0],split="calibration")
        o=PrivateGroupOracle(s,CAL_SPECS[0][3],0)
        value=o.reveal(0,1)
        with self.assertRaisesRegex(MeasurementContractError,"IDS_DIFFER"):
            o.finish({})
        with self.assertRaisesRegex(MeasurementContractError,"VALUES_DIFFER"):
            o.finish({0:(value+1.,)})
        with self.assertRaisesRegex(MeasurementContractError,"BUDGET"):
            o.finish({0:(value,)})

    def test_full_budget_random_campaign_with_only_revealed_values(self):
        r=run_campaign("calibration",CAL_SPECS[0],"random_bundled",0)
        self.assertEqual(r["measurement_count"],48)
        self.assertEqual(r["completed_designs"],16)
        self.assertEqual(r["incomplete_designs"],0)
        self.assertFalse(r["latent_outcomes_passed_to_selector"])
        self.assertFalse(r["future_responses_passed_to_selector"])
        self.assertGreaterEqual(r["evidence_score"],0.)
        self.assertGreaterEqual(r["latent_recommendation_regret"],0.)

    def test_immediate_acquisition_cannot_inspect_unseen_outcomes(self):
        s=make_group_source(CAL_SPECS[0],split="calibration")
        seed=CAL_SPECS[0][3]
        ids=initial_geometry_ids(48,seed)
        acquired={i:tuple(map(float,s.outcomes[i])) for i in ids}
        other=s.outcomes.copy()
        other[[i for i in range(48) if i not in ids]]+=1e4
        altered=replace(s,outcomes=other)
        for policy in POLICIES:
            a=propose_action(policy,s.descriptors,acquired,seed=seed,step=0)
            b=propose_action(policy,altered.descriptors,acquired,seed=seed,step=0)
            self.assertEqual(a,b)
        self.assertEqual(list(inspect.signature(propose_action).parameters),
                         ["policy","descriptors","observed","seed","step"])

    def test_fixed_threshold_selection_respects_coverage_and_error_cap(self):
        rows=fake_rows()
        for policy in POLICIES:
            sample=[r for r in rows if r["policy"]==policy]
            fit=select_threshold(sample,.5)
            self.assertEqual(fit["denominator"],8)
            self.assertLessEqual(fit["coverage"],.5)
            self.assertLessEqual(fit["high_regret_rate"] or 0.,.25)
            self.assertEqual(fit["accepted"],4)

    def test_all_bad_calibration_abstains_instead_of_faking_coverage(self):
        sample=[r for r in fake_rows() if r["policy"]==POLICIES[0]]
        for r in sample:r["high_regret_error"]=True
        fit=select_threshold(sample,.5)
        self.assertEqual(fit["accepted"],0)
        self.assertIsNone(fit["high_regret_rate"])

    def test_evaluation_labels_are_rejected_from_threshold_fitting(self):
        rows=fake_rows()
        rows[0]["split"]="evaluation"
        with self.assertRaisesRegex(MeasurementContractError,"CALIBRATION_ONLY"):
            calibrate_policy_thresholds(rows)
        rows=fake_rows()
        rows[0]["group"]=EVAL_SPECS[0][0]
        with self.assertRaises(MeasurementContractError):
            calibrate_policy_thresholds(rows)
        rows=fake_rows()[:-1]
        with self.assertRaises(MeasurementContractError):
            calibrate_policy_thresholds(rows)

    def test_duplicate_groups_and_represented_ties_are_conservative(self):
        rows=fake_rows()
        rows[0]["group"]=rows[1]["group"]
        rows[0]["order_variant"]=rows[1]["order_variant"]
        rows[0]["policy"]=rows[1]["policy"]
        with self.assertRaises(MeasurementContractError):
            calibrate_policy_thresholds(rows)
        tied=[r for r in fake_rows() if r["policy"]==POLICIES[0]]
        for r in tied:r["evidence_score"]=1.
        result=select_threshold(tied,.5)
        self.assertEqual(result["accepted"],0)

    def test_calibration_document_detects_changed_scores_and_thresholds(self):
        frozen=fake_document()
        self.assertEqual(verify_calibration_document(frozen),frozen["thresholds"])
        forged=copy.deepcopy(frozen)
        forged["calibration_rows"][0]["evidence_score"]+=2
        with self.assertRaisesRegex(MeasurementContractError,"ROWS_TAMPERED"):
            verify_calibration_document(forged)
        forged=copy.deepcopy(frozen)
        forged["thresholds"][POLICIES[0]]["0.50"]["threshold"]+=1
        with self.assertRaisesRegex(MeasurementContractError,"THRESHOLDS_TAMPERED"):
            verify_calibration_document(forged)

    def test_staged_evaluation_constructs_only_evaluation_sources(self):
        frozen=fake_document()
        calls=[]
        def stand_in(split,spec,policy,variant):
            calls.append((split,spec[0],policy,variant))
            return {"split":split,"group":spec[0],"policy":policy,
                    "order_variant":variant,"evidence_score":1.,
                    "latent_recommendation_regret":.1,"high_regret_error":False,
                    "incomplete_designs":0,"stranded_partial_responses":0,
                    "completion_interventions":0,"measurement_count":48}
        with patch('scripts.bhs_v125_disjoint_calibration.run_campaign',side_effect=stand_in):
            result=build_evaluation(frozen,calibration_file_sha256='a'*64)
        self.assertEqual(len(calls),len(EVAL_SPECS)*len(ORDER_VARIANTS)*len(POLICIES))
        self.assertTrue(all(split=='evaluation' and group in {s[0] for s in EVAL_SPECS}
                            for split,group,_,_ in calls))
        self.assertEqual(result["stage"],"evaluation")
        self.assertTrue(all(v is False for k,v in result["hard_gates"].items()
                            if k!='development_only'))
        self.assertTrue(result["hard_gates"]["development_only"])

    def test_zero_coverage_metrics_explicitly_keep_denominators(self):
        rows=[{"evidence_score":0.,"latent_recommendation_regret":.8,
               "high_regret_error":True,"incomplete_designs":2,
               "stranded_partial_responses":3,"completion_interventions":1}]
        m=_metrics(rows,threshold=1.)
        self.assertEqual((m["accepted"],m["denominator"],m["coverage"]),(0,1,0.))
        self.assertIsNone(m["conditional_mean_latent_regret"])
        self.assertIsNone(m["accepted_high_regret_error_rate"])
        self.assertEqual(m["mean_abstention_adjusted_loss"],.5)

    def test_untrusted_calibration_file_cannot_open_evaluation(self):
        bad=fake_document()
        bad["calibration_groups"]=[999]
        with patch('scripts.bhs_v125_disjoint_calibration.run_campaign') as acquire:
            with self.assertRaises(MeasurementContractError):
                build_evaluation(bad,calibration_file_sha256='f'*64)
            acquire.assert_not_called()

    def test_protected_seeds_and_nonautomatic_cli(self):
        self.assertEqual(main([]),0)
        self.assertTrue(HARD_GATES["development_only"])
        self.assertFalse(HARD_GATES["claim_of_superiority"])
        with self.assertRaises(MeasurementContractError):
            make_group_source((101,"ridge","constant",10000),split="calibration")


if __name__=='__main__':
    unittest.main()
