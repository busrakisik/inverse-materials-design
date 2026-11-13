"""V12.18 strictly manufactured two-model evidence/decision tests.

Do not import physical response datasets or infer real physical mechanisms.
"""
import ast
import math
from pathlib import Path
import unittest
import numpy as np

from scripts import bhs_v1218_dual_predictive_hypotheses as a


def simple_public():
    return {
        "ref": {"n": 12, "theta_deg": 90, "r_mm": 2.5, "t_mm": 1.0},
        "coupled": {"n": 12, "theta_deg": 120, "r_mm": 2.5, "t_mm": 1.3},
        "reverse": {"n": 8, "theta_deg": 60, "r_mm": 2.2, "t_mm": 0.7},
        "other": {"n": 10, "theta_deg": 100, "r_mm": 2.8, "t_mm": 0.9},
    }


class DuelTests(unittest.TestCase):
    def test_hypotheses_are_different_nested_forms_not_mechanisms(self):
        base=a.normalize_design(simple_public()["coupled"])
        x0=a._features(base,"H_ADD")
        x1=a._features(base,"H_TWIST_THICKNESS")
        self.assertEqual(x0.shape,(5,))
        self.assertEqual(x1.shape,(6,))
        self.assertNotEqual(x1[-1],0)
        self.assertTrue(np.array_equal(x0,x1[:-1]))

    def test_constant_reference_design(self):
        self.assertTrue(np.array_equal(a.normalize_design(simple_public()["ref"]),
                                       np.zeros(4)))

    def test_prior_weights_equal(self):
        _, history, models, w=a.fit_from_visible_history(simple_public(),[])
        self.assertEqual(history,[])
        self.assertEqual(w,{"H_ADD":0.5,"H_TWIST_THICKNESS":0.5})
        self.assertTrue(all(m.log_evidence==0 for m in models))

    def test_analytic_conjugate_intercept_update(self):
        _, _, models, w=a.fit_from_visible_history(simple_public(),[("ref",10.0)])
        for model in models:
            self.assertAlmostEqual(model.mean[0],8.0,places=10)
            self.assertAlmostEqual(model.cov[0,0],20.0,places=10)
            self.assertAlmostEqual(model.predict(np.zeros(4))[1],45.0,places=10)
        self.assertAlmostEqual(w["H_ADD"],0.5,places=12)

    def test_physical_candidate_interaction_changes_prior_variance(self):
        base=a.normalize_design(simple_public()["coupled"])
        m0=a.ConditionalLinearModel.initial("H_ADD")
        m1=a.ConditionalLinearModel.initial("H_TWIST_THICKNESS")
        self.assertAlmostEqual(m0.predict(base)[0],m1.predict(base)[0])
        self.assertGreater(m1.predict(base)[1],m0.predict(base)[1])

    def test_interacting_observation_updates_model_odds(self):
        _, _, models, w=a.fit_from_visible_history(
            simple_public(),[("coupled",12.0)])
        self.assertNotAlmostEqual(w["H_ADD"],0.5,places=8)
        self.assertAlmostEqual(sum(w.values()),1.0,places=12)
        self.assertTrue(all(np.isfinite(m.mean).all() for m in models))

    def test_repeat_visits_affect_only_previous_responses(self):
        pool=simple_public()
        first=a.choose_next(pool,[])
        selected=first["selected_candidate_id"]
        second=a.choose_next(pool,[(selected,12.0)])
        self.assertNotEqual(selected,second["selected_candidate_id"])
        self.assertEqual(second["previously_revealed_count"],1)

    def test_repeated_selection_has_exact_same_output(self):
        pool=simple_public()
        obs=[("ref",8.0)]
        self.assertEqual(a.choose_next(pool,obs),a.choose_next(pool,obs))

    def test_no_candidate_order_leakage(self):
        pool=simple_public()
        backwards=dict(reversed(list(pool.items())))
        a1=a.choose_next(pool,[])
        a2=a.choose_next(backwards,[])
        self.assertEqual(a1["selected_candidate_id"],a2["selected_candidate_id"])
        self.assertEqual(a1["candidate_information_gain_nats"],
                         a2["candidate_information_gain_nats"])

    def test_no_unrevealed_labels_could_be_read(self):
        pool=simple_public()
        self.assertTrue(all(set(v)==set(a.FEATURES) for v in pool.values()))
        result=a.choose_next(pool,[])
        self.assertFalse(result["scored_validation_allowed"])
        self.assertFalse(result["decision_chronology_authenticated"])
        self.assertFalse(result["hypotheses_are_physical_mechanisms"])
        self.assertFalse(result["real_response_cost_verified"])

    def test_model_selection_not_optimized_toughness(self):
        result=a.choose_next(simple_public(),[])
        self.assertEqual(result["selection_objective"],
                         "ONE_STEP_MODEL_ID_INFORMATION_GAIN_NOT_TOUGHNESS_OPTIMIZATION")
        self.assertGreaterEqual(result["selection_information_gain_nats"],0)
        self.assertLessEqual(result["selection_information_gain_nats"],math.log(2)+1e-8)

    def test_eig_of_reference_prior_has_zero_no_interaction(self):
        pool=simple_public()
        _,_,models,w=a.fit_from_visible_history(pool,[])
        gain=a.expected_model_information_gain(a.normalize_design(pool["ref"]),
                                               models,w)
        self.assertAlmostEqual(gain,0.0,places=8)

    def test_quadrature_rule_cannot_be_changed_after_frozen_protocol(self):
        _,_,models,w=a.fit_from_visible_history(simple_public(),[])
        with self.assertRaisesRegex(a.HypothesisContractError,"QUADRATURE_RULE_FROZEN"):
            a.expected_model_information_gain(
                a.normalize_design(simple_public()["coupled"]),models,w,8)

    def test_all_history_observed_candidates_rejected(self):
        with self.assertRaisesRegex(a.HypothesisContractError,"NO_UNOBSERVED_CANDIDATES"):
            a.choose_next({"ref":simple_public()["ref"]},[("ref",10.0)])

    def test_duplicate_label_blocked(self):
        with self.assertRaisesRegex(a.HypothesisContractError,"UNKNOWN_DUPLICATE"):
            a.choose_next(simple_public(),[("ref",10.0),("ref",12.0)])

    def test_unselected_id_label_blocked(self):
        with self.assertRaisesRegex(a.HypothesisContractError,"UNKNOWN_DUPLICATE"):
            a.choose_next(simple_public(),[("not-existing",10.0)])

    def test_public_design_cannot_contain_measured_toughness(self):
        pool=simple_public()
        pool["coupled"]["toughness_j"]=30.0
        with self.assertRaisesRegex(a.HypothesisContractError,"EXACT_PUBLIC_DESIGN_FIELDS_REQUIRED"):
            a.choose_next(pool,[])

    def test_invalid_candidate_dimensions_rejected(self):
        for changes in ({"n":8.5},{"n":0},{"theta_deg":200},{"r_mm":-0.1},
                        {"r_mm":0.6,"t_mm":0.7},{"theta_deg":float("nan")},
                        {"theta_deg":True}):
            with self.subTest(changes=changes):
                pool=simple_public()
                pool["coupled"].update(changes)
                with self.assertRaises(a.HypothesisContractError):
                    a.choose_next(pool,[])

    def test_invalid_measurement_blocks_update(self):
        for v in (float("nan"),float("inf"),-1.0,None,True,"secret"):
            with self.subTest(measurement=v):
                with self.assertRaises(a.HypothesisContractError):
                    a.fit_from_visible_history(simple_public(),[("ref",v)])

    def test_invalid_priors_and_hypothesis_identifier_rejected(self):
        with self.assertRaises(a.HypothesisContractError):
            a.ConditionalLinearModel.initial("meaningless-new-physical-claim")
        with self.assertRaises(a.HypothesisContractError):
            a._features(np.zeros(4),"unregistered")

    def test_frozen_model_hyperparameters(self):
        self.assertEqual(a.MODEL_PRIORS,(0.5,0.5))
        self.assertEqual(a.COEFF_PRIOR_SD_J,10.0)
        self.assertEqual(a.ASSUMED_NOISE_SD_J,5.0)
        self.assertEqual(a.QUADRATURE_POINTS,16)

    def test_no_source_download_or_source_outcomes_imported(self):
        source=Path(a.__file__).read_text()
        tree=ast.parse(source)
        modules=[n.module or "" for n in ast.walk(tree)
                 if isinstance(n,ast.ImportFrom)]
        imports=[alias.name for n in ast.walk(tree) if isinstance(n,ast.Import)
                 for alias in n.names]
        forbidden=("requests","urllib","ucimlrepo","pandas","socket","subprocess")
        self.assertFalse(any(m.startswith(forbidden) for m in modules+imports))
        self.assertNotIn("fetch_source(",source)
        self.assertNotIn("read_csv(",source)

    def test_repeat_observation_does_not_mutate_caller_features(self):
        pool=simple_public()
        original={x:dict(d) for x,d in pool.items()}
        obs=[("ref",12.0)]
        first=a.choose_next(pool,obs)
        self.assertEqual(pool,original)
        self.assertEqual(obs,[("ref",12.0)])
        self.assertFalse(first["independent_holdout_used"])

    def test_empty_and_malformed_pool_rejected(self):
        for pool in ([], {}, None):
            with self.subTest(pool=pool):
                with self.assertRaises(a.HypothesisContractError):
                    a.choose_next(pool,[])

    def test_two_hypothesis_update_not_mcts(self):
        result=a.choose_next(simple_public(),[("ref",8.0)])
        self.assertTrue(result["synthetic_protocol_only"])
        self.assertFalse(result["full_bhs_fair_comparison_ready"])
        self.assertFalse(result["physical_mechanisms_identified"])
        self.assertNotIn("mcts_selected_action",result)


if __name__ == "__main__":
    unittest.main()
