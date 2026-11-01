import copy
import hashlib
import unittest
from scripts.matbench_split_gate import build_manifest, validate_manifest, EXPECTED_SOURCE_SHA, SALT

class Element:
    def __init__(self,s):self.s=s
    def __str__(self):return self.s
class FakeComposition:
    def __init__(self,formula):
        if not formula or not formula.startswith('X'):
            raise ValueError('invalid fixture')
        self.s=formula
        # X0 and X1 are distinct chemical systems; repeated duplicates modeled separately
        self.elements=[Element('X'),Element(formula[1:])]
        self.reduced_formula=formula
    def __bool__(self):return True

def make(n=100):return [f'X{i}' for i in range(n)]
def mk(formulas=None):
    fs=make() if formulas is None else formulas
    return build_manifest(fs,source_sha256=EXPECTED_SOURCE_SHA,composition_factory=FakeComposition,expected_rows=len(fs))
class SplitGateTests(unittest.TestCase):
    def test_complete_disjoint(self):
        m=mk();ids=[set(m['partitions'][p]['original_row_indices']) for p in ('train','validation','test')]
        self.assertEqual(set.union(*ids),set(range(100)))
        self.assertTrue(all(not ids[i]&ids[j] for i in range(3) for j in range(i+1,3)))
    def test_repeatable(self):self.assertEqual(mk(),mk())
    def test_order_independent_group_assignment(self):
        a=mk(make(100));b=mk(list(reversed(make(100))))
        def labels(m,formulas):return {formulas[i]:p for p,v in m['partitions'].items() for i in v['original_row_indices']}
        self.assertEqual(labels(a,make(100)),labels(b,list(reversed(make(100)))))
    def test_label_blind(self):
        m=mk();self.assertFalse(m['label_accessed_by_splitter']);self.assertFalse(m['labels_in_manifest']);self.assertFalse(m['benchmark_run']);self.assertNotIn('gap expt',str(m))
    def test_wrong_sha(self):
        with self.assertRaises(ValueError):build_manifest(make(),source_sha256='0'*64,composition_factory=FakeComposition,expected_rows=100)
    def test_wrong_salt(self):
        with self.assertRaises(ValueError):build_manifest(make(),source_sha256=EXPECTED_SOURCE_SHA,composition_factory=FakeComposition,salt='changed',expected_rows=100)
    def test_duplicate_reduced_formula_rejected(self):
        with self.assertRaises(ValueError):mk(make(99)+['X0'])
    def test_invalid_formula_rejected(self):
        with self.assertRaises(ValueError):mk(make(99)+['broken'])
    def test_too_few_groups_rejected(self):
        with self.assertRaises(ValueError):mk(make(2))
    def test_overlapping_indices_rejected(self):
        m=mk();i=m['partitions']['train']['original_row_indices'][0]
        m['partitions']['test']['original_row_indices'].append(i)
        # production validator expects full 4604, but overlap detected first
        with self.assertRaisesRegex(ValueError,'overlapping'):validate_manifest(m)

if __name__=='__main__':unittest.main()
