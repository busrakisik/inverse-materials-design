"""Synthetic adversarial probes; NEVER put real labels/secrets inside image."""
import json, os, pathlib, socket, sys

def probe(mode):
    if mode == 'identity':
        return {'uid': os.geteuid(), 'gid': os.getegid()}
    if mode == 'network':
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.8)
        try:
            s.connect(('1.1.1.1', 443))
            return {'network_connected': True}
        except OSError:
            return {'network_connected': False}
        finally: s.close()
    if mode == 'filesystem':
        try:
            pathlib.Path('/opt/forbidden-write').write_text('probe')
            return {'wrote_rootfs': True}
        except OSError:
            return {'wrote_rootfs': False}
    if mode == 'secret':
        return {'secret_present': pathlib.Path('/private/held_out_labels.json').exists(),
                'secret_env_present': 'BHS_TEST_SECRET' in os.environ}
    if mode == 'privileges':
        status = pathlib.Path('/proc/self/status').read_text()
        vals = {k: v.strip() for line in status.splitlines() if ':' in line for k,v in [line.split(':',1)]}
        return {'no_new_privs': vals.get('NoNewPrivs'), 'cap_eff': vals.get('CapEff')}
    if mode == 'tmp':
        p=pathlib.Path('/tmp/bhs-probe');p.write_text('ok');v=p.read_text();p.unlink()
        return {'scratch_ok': v=='ok'}
    if mode == 'pid':
        return {'pid': os.getpid()}
    raise ValueError('unknown mode')

if __name__=='__main__':
    print(json.dumps(probe(sys.argv[1]),sort_keys=True))
