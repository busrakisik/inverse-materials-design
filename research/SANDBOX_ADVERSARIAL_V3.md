# BHS Synthetic Sandbox & Adversarial Gate v3

**SYNTHETIC PROBES ONLY — NO REAL LABELS — NOT A MATERIALS BENCHMARK.**

This gate builds a standalone probe-only Docker image containing `sandbox_probe_v3.py`, with no project source tree, datasets, credentials or benchmark labels copied or mounted. Each probe container runs as numeric user 65534, without networking, with a read-only rootfs, all Linux capabilities dropped, no-new-privileges enabled, PID/memory/CPU constraints and a bounded writable /tmp. The test fails if Docker is absent rather than skipping security checks. 10 probes verify the configuration and selected behaviors.

## Limits / threat model
- This is an isolation **demonstrator**, NOT a certified security boundary against arbitrary malicious code. Standard Docker isolation relies on the host kernel and Docker daemon configuration; container escape vulnerabilities, daemon access, exposed sockets, kernel issues and ambient runner privileges are out of scope.
- The test only checks a probe image, not the existing BHS Oracle worker or the ML/physics stack. **Do not interpret the gate as authorization to run hidden benchmark labels with BHS.** Moving to a real-data benchmark needs a frozen threat model, a pre-reviewed image with digest pinning/SBOM, verified mount and environment allowlists, explicit side-channel assumptions, runtime resource enforcement measurements and trusted independent held-out evaluation.
- Disabling container network does not establish that all exfiltration channels are eliminated. Future integration should keep hidden labels entirely outside the worker host/namespace and provide observations via a metered protocol.
- `--memory` and `--pids-limit` are configured here but stress/resource isolation under adversarial fork bombs is not experimentally validated. CI host runner should be treated as disposable.
- Uses `python:3.11-slim` tag for reproducible demonstration; pin a reviewed digest before any production use.

## Reproduce

On a disposable Linux machine with Docker daemon and permissions:
`python -m unittest discover -s tests -p 'test_sandbox_v3.py' -v`

Do not merge to main or mint a Zenodo DOI based only on these tests. Preserve the original 12+8+10 CI contracts. This v3 gate adds 10 separate tests; it does not claim to verify their current status.
