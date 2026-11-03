# BHS Historical Artifact Content Audit v1

**STATUS: PILOT_ARTIFACT_VERIFIED_ONLY / NO_HOLDOUT_APPROVAL / SYNTHETIC_ONLY**

Audits the actual **existing** paired pilot ZIP file (1,800 recorded observations), not arbitrary code literals. Requires a local artifact ZIP from the successful GitHub Actions pilot. Confirms paired `(scenario, task seed, budget, policy)` coverage, unique candidate actions, budget, manifest, and observed task seeds. Produces a SHA-256-linked audit report. Does not evaluate any new task or holdout label.

## Evidence currently verified
The archived pilot `bhs-synthetic-paired-pilot-v1` from run `41456995112` contains exactly 1,800 experiment rows and task seeds 0–29. These are disjoint from the *proposed* validation seeds 10000–10099. This only establishes the pilot ZIP's seed usage, not the absence of seed reuse in all history.

## Reproduce
Download the original artifact from https://github.com/busrakisik/inverse-materials-design/actions/runs/41456995112/artifacts/13146289436 and run:

`python -m scripts.artifact_content_audit_v1 --archive path/to/actual-pilot.zip`

Run contract tests with `python -m unittest discover -s tests -p 'test_artifact_content_audit_v1.py' -v`.

The CI only runs tests and records successful unit-test results. It intentionally does not fetch the external ZIP; actual pilot analysis is explicitly an offline step. Reading ZIP contents does not create a security boundary for arbitrary malicious files; use only trusted sources and a disposable environment. No final freeze, independent validation, or physical result is asserted.
