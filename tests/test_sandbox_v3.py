"""Fail closed: requires functioning Docker daemon; no skip on missing engine."""
import json, os, pathlib, shutil, subprocess, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
IMAGE = 'bhs-sandbox-probe:v3'

def docker(*args, timeout=40):
    return subprocess.run(['docker', *args], text=True, capture_output=True, timeout=timeout)

def secure_args(mode):
    return ['run', '--rm', '--network', 'none', '--read-only', '--cap-drop', 'ALL',
            '--security-opt', 'no-new-privileges', '--user', '65534:65534',
            '--pids-limit', '64', '--memory', '256m', '--cpus', '1',
            '--tmpfs', '/tmp:rw,nosuid,noexec,size=16m,mode=1777',
            '--env', 'PYTHONDONTWRITEBYTECODE=1', IMAGE, mode]

class DockerSandboxV3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if shutil.which('docker') is None:
            raise RuntimeError('FAIL CLOSED: Docker unavailable')
        info = docker('info', '--format', '{{.ServerVersion}}')
        if info.returncode: raise RuntimeError('FAIL CLOSED: Docker daemon unavailable: '+info.stderr[-300:])
        build = docker('build', '-f', str(ROOT/'scripts/Dockerfile.sandbox-v3'),
                       '-t', IMAGE, str(ROOT/'scripts'), timeout=120)
        if build.returncode: raise RuntimeError('FAIL CLOSED: image build failed: '+build.stderr[-500:])

    def run_probe(self, mode):
        r = docker(*secure_args(mode))
        self.assertEqual(r.returncode, 0, r.stderr[-500:])
        return json.loads(r.stdout.strip())

    def test_nonroot(self):
        self.assertEqual(self.run_probe('identity'), {'uid': 65534, 'gid': 65534})
    def test_network_disabled(self):
        self.assertFalse(self.run_probe('network')['network_connected'])
    def test_root_filesystem_readonly(self):
        self.assertFalse(self.run_probe('filesystem')['wrote_rootfs'])
    def test_labels_not_mounted_or_env(self):
        r=self.run_probe('secret');self.assertFalse(r['secret_present']);self.assertFalse(r['secret_env_present'])
    def test_no_new_privileges(self):
        self.assertEqual(self.run_probe('privileges')['no_new_privs'], '1')
    def test_no_effective_caps(self):
        self.assertEqual(int(self.run_probe('privileges')['cap_eff'],16), 0)
    def test_writable_bounded_tmp(self):
        self.assertTrue(self.run_probe('tmp')['scratch_ok'])
    def test_container_pid_namespace(self):
        self.assertEqual(self.run_probe('pid')['pid'],1)
    def test_enforced_config(self):
        args=secure_args('identity');s=' '.join(args)
        for x in ('--network none','--read-only','--cap-drop ALL','no-new-privileges',
                  '--pids-limit 64','--memory 256m','--cpus 1','--tmpfs /tmp:'):
            self.assertIn(x,s)
    def test_denied_image_shell_execution(self):
        # Entrypoint is a fixed probe, unknown modes fail rather than acting as a shell.
        r=docker(*secure_args('not-a-mode'))
        self.assertNotEqual(r.returncode,0)

if __name__=='__main__': unittest.main()
