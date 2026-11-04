import math
import unittest
from scripts.competing_hypotheses_v1 import (
    MODELS, STATUS, CompetingHypothesesPolicyV1, entropy,
    expected_information_gain, fixed_development_demo, normalize_log_weights,
    posterior, prediction, update_probs,
)


class CompetingHypothesesTests(unittest.TestCase):
    public = {'zero': (0.0,), 'negative': (-1.0,), 'positive': (1.0,), 'middle': (0.5,)}

    def test_three_finite_mechanisms(self):
        self.assertEqual(MODELS, ('linear', 'quadratic', 'oscillatory'))
        self.assertAlmostEqual(prediction('quadratic', -0.5), 0.25)
        self.assertAlmostEqual(prediction('linear', -0.5), -0.5)
        self.assertAlmostEqual(prediction('oscillatory', 0.0), 0)

    def test_uniform_initial_belief(self):
        probs = posterior(self.public, [])
        for p in probs:
            self.assertAlmostEqual(p, 1/3)

    def test_posterior_concentrates_on_observed_mechanism(self):
        obs = [('negative', 1.0), ('positive', 1.0)]
        probs = posterior(self.public, obs, noise_std=0.1)
        self.assertGreater(probs[1], 0.99)

    def test_bayes_update_normalized(self):
        p = update_probs((1/3, 1/3, 1/3), -1.0, 1.0, 0.1)
        self.assertAlmostEqual(sum(p), 1.0)
        self.assertGreater(p[1], p[0])

    def test_entropy(self):
        self.assertAlmostEqual(entropy((1/3, 1/3, 1/3)), math.log(3))
        self.assertAlmostEqual(entropy((1, 0, 0)), 0)

    def test_zero_feature_uninformative(self):
        self.assertAlmostEqual(expected_information_gain((1/3,)*3, 0), 0, places=9)

    def test_informative_feature_has_positive_gain(self):
        self.assertGreater(expected_information_gain((1/3,)*3, -1, 0.15), 0.1)

    def test_chooses_nonzero_with_uniform_prior(self):
        policy = CompetingHypothesesPolicyV1()
        self.assertNotEqual(policy.choose(self.public, ()), 'zero')
        self.assertFalse(policy.last_diagnostics['scored_validation_allowed'])

    def test_does_not_repeat_observation(self):
        policy = CompetingHypothesesPolicyV1()
        chosen = policy.choose(self.public, ())
        self.assertNotEqual(policy.choose(self.public, ((chosen, 0.3),)), chosen)

    def test_reproducible(self):
        a = CompetingHypothesesPolicyV1()
        b = CompetingHypothesesPolicyV1()
        self.assertEqual(a.choose(self.public, ()), b.choose(self.public, ()))
        self.assertEqual(a.last_diagnostics, b.last_diagnostics)

    def test_reject_duplicate_observation(self):
        with self.assertRaises(ValueError):
            posterior(self.public, [('negative', 1), ('negative', 1)])

    def test_reject_nonfinite_and_unknown_public(self):
        with self.assertRaises(ValueError):
            posterior({'bad': (float('nan'),)}, ())
        with self.assertRaises(ValueError):
            posterior(self.public, [('missing', 1)])
        with self.assertRaises(ValueError):
            prediction('missing', 0.3)

    def test_reject_invalid_probabilities(self):
        with self.assertRaises(ValueError):
            entropy((1, 1, 1))
        with self.assertRaises(ValueError):
            normalize_log_weights((0, float('nan'), 0))

    def test_reject_invalid_params(self):
        with self.assertRaises(ValueError):
            CompetingHypothesesPolicyV1(quantiles=1)
        with self.assertRaises(ValueError):
            CompetingHypothesesPolicyV1(noise_std=0)
        with self.assertRaises(ValueError):
            expected_information_gain((1/3,)*3, 0.5, quantiles=True)

    def test_exhausted_pool(self):
        p = {'only': (0.3,)}
        with self.assertRaises(ValueError):
            CompetingHypothesesPolicyV1().choose(p, [('only', 0)])

    def test_fixed_demo_no_holdout(self):
        report = fixed_development_demo()
        self.assertEqual(len(report['observations']), 5)
        self.assertFalse(report['scored_validation_allowed'])
        self.assertFalse(report['independent_holdout_used'])
        self.assertEqual(report['status'], STATUS)


if __name__ == '__main__':
    unittest.main()
