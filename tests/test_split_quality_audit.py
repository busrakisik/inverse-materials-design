import unittest
from scripts.split_quality_audit import inspect_split,SHA
class E:
    def __init__(self,s):self.s=s
    def __str__(self):return self.s
class C:
    def __init__(self,f):self.elements=[E(x) for x in f.split('-')]
def data():
    f=['Li-O']*2302+['Fe-O']*2302
    m={'dataset':'matbench_expt_gap','source_compressed_sha256':SHA,'labels_in_manifest':False,'label_accessed_by_splitter':False,'benchmark_run':False,'partitions':{
        'train':{'original_row_indices':list(range(2302)),'row_count':2302,'chemical_system_count':1},
        'validation':{'original_row_indices':list(range(2302,3453)),'row_count':1151,'chemical_system_count':1},
        'test':{'original_row_indices':list(range(3453,4604)),'row_count':1151,'chemical_system_count':1}}}
    # make validation and test different chem systems
    f[3453:]=['P-O']*1151
    return m,f
class ContractTests(unittest.TestCase):
    def test_valid(self):
        m,f=data();r=inspect_split(m,f,C,SHA);self.assertEqual(r['total_groups'],3);self.assertFalse(r['benchmark_run'])
    def test_hash_mismatch(self):
        m,f=data();self.assertRaises(ValueError,inspect_split,m,f,C,'0'*64)
    def test_coverage(self):
        m,f=data();m['partitions']['test']['original_row_indices'].pop();self.assertRaises(ValueError,inspect_split,m,f,C,SHA)
    def test_leakage_detected(self):
        m,f=data();f[-1]='Li-O';self.assertRaises(ValueError,inspect_split,m,f,C,SHA)
    def test_label_flag(self):
        m,f=data();m['labels_in_manifest']=True;self.assertRaises(ValueError,inspect_split,m,f,C,SHA)
    def test_group_count(self):
        m,f=data();m['partitions']['train']['chemical_system_count']=2;self.assertRaises(ValueError,inspect_split,m,f,C,SHA)
if __name__=='__main__':unittest.main()
