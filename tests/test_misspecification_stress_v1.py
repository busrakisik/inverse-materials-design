"""Development-only contracts; forbid interpreting descriptive diagnostics as certification."""
import math
import unittest
from scripts import misspecification_stress_v1 as m


class StressTests(unittest.TestCase):
    def test_six_scenarios(self):
        self.assertEqual(len(m.SCENARIOS),6)

    def test_fixed_count(self):
        p, ss = m.make_fixed_stress_streams()
        self.assertEqual(len(p),m.N)
        self.assertTrue(all(len(s)==m.N for s in ss.values()))

    def test_reproducible_streams(self):
        self.assertEqual(m.make_fixed_stress_streams(),m.make_fixed_stress_streams())

    def test_distinct_scenarios(self):
        _, ss=m.make_fixed_stress_streams()
        self.assertNotEqual(ss['in_family'],ss['out_of_family_step'])
        self.assertNotEqual(ss['in_family'],ss['underreported_noise'])

    def test_declared_std_identical(self):
        _, ss=m.make_fixed_stress_streams()
        self.assertTrue(all(r[2]==m.DECLARED_STD for s in ss.values() for r in s))

    def test_valid_descriptor_domain(self):
        p,_=m.make_fixed_stress_streams()
        self.assertTrue(all(-1<=x[0]<=1 for x in p.values()))

    def test_invalid_unknown_scenario(self):
        with self.assertRaises(ValueError):m.make_fixed_stress_streams(['holdout'])

    def test_invalid_duplicate_scenario(self):
        with self.assertRaises(ValueError):m.make_fixed_stress_streams(['in_family','in_family'])

    def test_empty_scenarios(self):
        with self.assertRaises(ValueError):m.run_stress([])

    def test_prequential_count(self):
        r=m.run_stress(['in_family'])
        self.assertEqual(r['scenarios']['in_family']['count'],m.N)

    def test_no_real_materials_and_holdout(self):
        r=m.run_stress(['in_family'])
        self.assertFalse(r['material_measurements_used'])
        self.assertFalse(r['benchmark_task_generator_called'])
        self.assertFalse(r['independent_holdout_used'])
        self.assertFalse(r['scored_validation_allowed'])

    def test_no_certification_flags(self):
        r=m.run_stress(['in_family'])
        for k in ('formal_out_of_family_detector','calibration_certified',
                  'statistical_significance_test_performed','automatic_warning_thresholds_enabled'):
            self.assertFalse(r[k])

    def test_coverage_splits(self):
        s=m.run_stress(['in_family'])['scenarios']['in_family']
        self.assertAlmostEqual((s['first_half_coverage']+s['second_half_coverage'])/2,s['empirical_coverage'])

    def test_metrics_finite(self):
        r=m.run_stress()
        self.assertTrue(all(math.isfinite(v) for s in r['scenarios'].values()
                            for v in s.values() if type(v) in (int,float)))

    def test_probs_bounded(self):
        r=m.run_stress()
        self.assertTrue(all(0<=s['final_max_model_probability']<=1 for s in r['scenarios'].values()))

    def test_pit_bounded(self):
        r=m.run_stress()
        self.assertTrue(all(0<=s['mean_pit']<=1 and 0<=s['extreme_pit_fraction']<=1
                            for s in r['scenarios'].values()))

    def test_coverage_gap(self):
        s=m.run_stress(['in_family'])['scenarios']['in_family']
        self.assertAlmostEqual(s['coverage_gap'],s['empirical_coverage']-.9)

    def test_run_reproducible(self):
        self.assertEqual(m.run_stress(),m.run_stress())

    def test_no_make_task_import(self):
        self.assertFalse(hasattr(m,'make_task'))

    def test_reject_invalid_records(self):
        with self.assertRaises(ValueError):m.summarize_records({'records':[],'count':0})


if __name__=='__main__':unittest.main()
