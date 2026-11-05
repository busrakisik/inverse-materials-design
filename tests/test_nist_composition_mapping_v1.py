import unittest
import numpy as np
from scripts.nist_composition_mapping_v1 import (
    normalize_composition_axis, target_vector, summarize_arrays, TARGETS,
    STATUS,
)


def fixture(c=None, coer=None, kerr=None):
    if c is None:
        c=np.array([[.2,.3,.5],[.1,.7,.2],[.4,.1,.5],[.7,.2,.1],[0,1,0]],dtype=float)
    n=5
    if coer is None:coer=np.arange(5,dtype=float).reshape(-1,1)
    if kerr is None:kerr=np.arange(5,dtype=float).reshape(1,-1)
    return {'C':c,'Coer':coer,'Kerr':kerr,'XRD':np.ones((n,7)), 'TTH':np.linspace(20,80,7)}

class NistMappingTests(unittest.TestCase):
    def test_counts(self):self.assertEqual(summarize_arrays(fixture())['samples_inferred'],5)
    def test_fraction_like(self):self.assertEqual(summarize_arrays(fixture())['composition']['fraction_like_rows'],5)
    def test_percent_like(self):
        a=fixture();a['C']=a['C']*100
        r=summarize_arrays(a)
        self.assertEqual(r['composition']['percentage_like_rows'],5)
        self.assertFalse(r['composition']['fraction_like_all_rows'])
    def test_transposed_composition(self):
        a=fixture();a['C']=a['C'].T
        self.assertEqual(summarize_arrays(a)['composition']['orientation'],'columns_are_samples')
    def test_target_vector_row_column(self):
        self.assertEqual(target_vector(np.arange(5).reshape(1,5),5,'Coer').shape,(5,))
        self.assertEqual(target_vector(np.arange(5).reshape(5,1),5,'Coer').shape,(5,))
    def test_target_vector_flat(self):self.assertEqual(target_vector(np.arange(5),5,'Kerr').shape,(5,))
    def test_bad_target_shape(self):
        with self.assertRaises(ValueError):target_vector(np.zeros((5,2)),5,'Coer')
    def test_bad_target_length(self):
        a=fixture();a['Kerr']=np.ones((1,4))
        with self.assertRaises(ValueError):summarize_arrays(a)
    def test_missing_field(self):
        a=fixture();a.pop('Kerr')
        with self.assertRaises(ValueError):summarize_arrays(a)
    def test_extra_field(self):
        a=fixture();a['magic']=np.array([3])
        with self.assertRaises(ValueError):summarize_arrays(a)
    def test_reject_complex(self):
        a=fixture();a['Coer']=np.arange(5,dtype=complex)
        with self.assertRaises(ValueError):summarize_arrays(a)
    def test_accept_uninterpreted_xrd_object(self):
        a=fixture();a['XRD']=np.array([['uninterpreted']],dtype=object)
        self.assertFalse(summarize_arrays(a)['xrd']['sample_axis_authoritatively_verified'])
    def test_nan_composition(self):
        a=fixture();a['C'][0,1]=np.nan
        r=summarize_arrays(a)
        self.assertEqual(r['composition']['nonfinite_rows'],1)
        self.assertEqual(r['targets']['Coer']['joint_finite_composition_count'],4)
    def test_nan_target(self):
        a=fixture();a['Coer'][2,0]=np.nan
        r=summarize_arrays(a)
        self.assertEqual(r['targets']['Coer']['missing_or_nonfinite_count'],1)
        self.assertEqual(r['targets']['Coer']['joint_finite_composition_count'],4)
    def test_inf_target(self):
        a=fixture();a['Kerr'][0,2]=np.inf
        self.assertEqual(summarize_arrays(a)['targets']['Kerr']['finite_count'],4)
    def test_ambiguous_composition(self):
        with self.assertRaises(ValueError):normalize_composition_axis(np.zeros((3,3)))
    def test_bad_composition_rank(self):
        with self.assertRaises(ValueError):normalize_composition_axis(np.zeros((5,)))
    def test_fail_closed_order(self):
        r=summarize_arrays(fixture())
        self.assertFalse(r['composition']['element_order_verified'])
        self.assertFalse(r['model_contract']['source_columns_mapped_to_model'])
    def test_fail_closed_scale(self):
        r=summarize_arrays(fixture())
        self.assertFalse(r['composition']['scale_authoritatively_verified'])
    def test_fail_closed_benchmark(self):
        r=summarize_arrays(fixture())
        self.assertFalse(r['scored_validation_allowed'])
        self.assertFalse(r['independent_holdout_used'])
        self.assertFalse(r['real_data_experiment_executed'])
        self.assertFalse(r['dataset_ready_for_bhs'])
    def test_reproducible(self):self.assertEqual(summarize_arrays(fixture()),summarize_arrays(fixture()))
    def test_status(self):self.assertEqual(summarize_arrays(fixture())['status'],STATUS)
    def test_no_model_import(self):
        from pathlib import Path
        source=Path('scripts/nist_composition_mapping_v1.py').read_text()
        self.assertNotIn('MultivariateBelief(',source)
        self.assertNotIn('make_task(',source)
        self.assertNotIn('run_grid(',source)

if __name__=='__main__':unittest.main()
