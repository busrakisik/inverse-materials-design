# BHS Process-Separated Synthetic Oracle — v1

**Status: SYNTHETIC_PROCESS_CONTRACT_ONLY / NOT_AN_OS_SANDBOX / REAL_TEST_LABELS_NOT_USED / NO_BENCHMARK_RUN.**

## Design
Trusted host holds fabricated labels, issues a structured JSON-lines public request to a separate child Python interpreter, and receives exactly one `candidate_id`. Child receives candidate IDs, remaining budget, and observations for *previously queried* candidates. Host meters budget, rejects unknown or repeated IDs, and returns a value-redacted trace. Each request and response is bounded to 16 KiB.

## Limitations and threat model
- Process separation is *not* a security perimeter by itself. An untrusted subprocess inherits ambient OS permissions, potentially inherited environment, file access, network and shared storage. No real held-out experimental labels may be loaded or made accessible to this worker. The host process also currently inherits ambient privileges. Stronger isolation needs least-privilege containers/process identities, explicit environment and file descriptor allowlisting, filesystem/network restriction, deadlines for unresponsive child reads, and review of all potential information channels.
- Current `readline` can block indefinitely on a malicious or hanging worker; the outer workflow timeout is needed, and a future implementation must enforce a per-message deadline. Do not claim malicious-worker resilience.
- This is not a trained policy or Bayesian hypothesis engine; the worker picks lexicographically first unqueried candidate.
- All inputs are fabricated numbers. No Matbench download or test evaluation.

## Next gate
Run the twelve synthetic contract tests in GitHub CI. Do not proceed to real-data oracle execution until a least-privilege boundary, timeouts, licensing, frozen protocol and adversarial checks are reviewed.
