import pathlib
import tempfile
import unittest
from scripts.synthetic_environment_lock_v1 import (
    PYTHON_PIN, SOURCES, build_manifest, check_imports, inspect_sources, sha256,
)

class EnvironmentLockTests(unittest.TestCase):
    def test_sha256_reference(self):
        self.assertEqual(sha256(b'abc'), 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')

    def test_stdlib_imports_allowed(self):
        self.assertEqual(check_imports('import hashlib, random\nfrom pathlib import Path\n'), [])

    def test_project_import_allowed(self):
        self.assertEqual(check_imports('from scripts.bayesian_only_policy_v1 import BayesianOnlyPolicyV1'), [])

    def test_third_party_import_rejected(self):
        self.assertTrue(check_imports('import torch'))

    def test_dynamic_import_rejected(self):
        self.assertTrue(check_imports("x = __import__('torch')"))

    def test_missing_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError): inspect_sources(pathlib.Path(tmp))

    def test_exact_patch_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_files(pathlib.Path(tmp))
            with self.assertRaises(ValueError):
                build_manifest(pathlib.Path(tmp), version=(3, 11, 8), system='Linux', machine='x86_64', commit='a'*40)

    def test_platform_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_files(pathlib.Path(tmp))
            with self.assertRaises(ValueError):
                build_manifest(pathlib.Path(tmp), version=PYTHON_PIN, system='Darwin', machine='arm64', commit='a'*40)

    def test_manifest_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            self._make_files(root)
            m = build_manifest(root, version=PYTHON_PIN, system='Linux', machine='x86_64', commit='a'*40)
            self.assertEqual(len(m['source_sha256']), 3)
            self.assertFalse(m['scored_validation_allowed'])
            self.assertFalse(m['environment_fully_hermetic'])
            self.assertEqual(m['external_pip_dependencies_required_by_scoped_modules'], [])

    @staticmethod
    def _make_files(root):
        for name in SOURCES:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('import math\n')

if __name__ == '__main__':
    unittest.main()
