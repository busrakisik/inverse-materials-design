import json
import subprocess
import sys
import unittest
from pathlib import Path

from scripts.policy_evaluator_isolation_v1 import run_demo, WORKER, STATUS


class ProcessBoundaryTests(unittest.TestCase):
    def test_dev_task_executed(self):
        r=run_demo()
        self.assertEqual(r['status'], STATUS)
        self.assertEqual(len(r['trace']), 5)
        self.assertEqual(len({x['candidate_id'] for x in r['trace']}), 5)
        self.assertTrue(r['separate_processes'])
    def test_repeatable(self):
        self.assertEqual(run_demo(),run_demo())
    def test_no_holdout(self):
        for seed in [10000,10001,0,30,True]:
            with self.subTest(seed=seed),self.assertRaises(ValueError):run_demo(task_seed=seed)
    def test_no_other_scenario(self):
        with self.assertRaises(ValueError):run_demo(scenario='multimodal')
    def test_budget_locked(self):
        for budget in [0,4,10,True]:
            with self.subTest(budget=budget),self.assertRaises(ValueError):run_demo(budget=budget)
    def test_policy_seed_locked(self):
        with self.assertRaises(ValueError):run_demo(policy_seed=14)
    def test_cannot_claim_sandbox(self):
        r=run_demo()
        self.assertIs(r['adversarial_worker_containment_proven'],False)
        self.assertIs(r['os_security_sandbox'],False)
        self.assertIs(r['scored_validation_allowed'],False)
        self.assertIs(r['holdout_tasks_generated'],False)
    def test_worker_rejects_extra_key(self):
        p=subprocess.run([sys.executable,'-I','-S',str(WORKER)],input='{"command":"initialize","seed":13,"_labels":{}}\n',text=True,capture_output=True,timeout=5)
        self.assertNotEqual(p.returncode,0)
        self.assertEqual(p.stdout,'')
    def test_worker_rejects_early_choose(self):
        p=subprocess.run([sys.executable,'-I','-S',str(WORKER)],input='{"command":"choose","public":{},"observations":[]}\n',text=True,capture_output=True,timeout=5)
        self.assertNotEqual(p.returncode,0)
    def test_worker_rejects_unknown_command(self):
        p=subprocess.run([sys.executable,'-I','-S',str(WORKER)],input='{"command":"evaluate"}\n',text=True,capture_output=True,timeout=5)
        self.assertNotEqual(p.returncode,0)

if __name__=='__main__': unittest.main()
