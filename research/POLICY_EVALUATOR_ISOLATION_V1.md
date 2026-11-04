# BHS Policy–Evaluator Process Boundary v1

**Scope:** A demonstrator with a single, already-development seed (`smooth`, task seed `7`, policy seed `13`, budget `5`). Does NOT execute held-out evaluation or make confirmatory claims.

## What is implemented
- Trusted parent constructs an ordinary synthetic `SyntheticTask`, retaining its full `_labels` dictionary in parent memory.
- Child worker (`scripts/policy_worker_v1.py`) runs a persistent `BayesianOnlyPolicyV1` object in its own Python process (`-I -S`).
- Line-delimited JSON IPC carries an initialization seed, public descriptors, and **only previously observed** candidate/value pairs. It does not serialize the full label map.
- Parent validates the selected candidate and looks up only its selected label, preserving the existing sequential query interface.
- Tests include fixed-development-task behavior, determinism, rejected holdout seeds, rejected malformed worker requests, and honest containment flags.

## Not proven or provided
- **Not a security sandbox.** A malicious child could potentially access files, `/proc`, networks, or other system resources; separate Python processes are not sufficient for attacker-grade isolation. No Docker/seccomp/user namespaces or file-system protection are configured.
- Parent has a blocking `readline`; a hostile worker can hang the parent. The workflow runs a known benign worker with a job timeout.
- Parent's communication has no cryptographic authenticity or integrity beyond local process pipes.
- Scope is synthetic only: not materials science validation, not MCTS, and not a superior method claim.
- Do not use the demo's five observations as independent evidence or select a new primary scenario based on them.

## Future gate
A genuine hostile-code security review needs sandboxed worker execution, deny-by-default network/filesystem policies, complete request/response logging, memory/cpu/wall-clock caps, and adversarial attempts to read unseen labels. Independent scored validation remains disallowed (`scored_validation_allowed=false`).
