# BHS Synthetic Process Oracle Deadline Gate v1

**Status: SYNTHETIC_ONLY / NOT_OS_SANDBOX / NO_REAL_LABELS / NO_MATERIALS_BENCHMARK.**

Separate from, and does not overwrite, the previously passing 12-test Process Oracle contract. Adds a POSIX-selector per-response deadline and child-process cleanup, synthetic adversarial fixtures, reduced child environment, and closed protocol checks.

The subprocess still has ambient filesystem/network privileges, inherited cwd/module visibility and the same Unix user privileges. Restricting environment variables is NOT a sandbox. A child can spawn descendants; this gate does not guarantee descendant termination. A malicious worker can still read any files accessible to its user, read network, and block writes. The deadline governs *response reads*, not all I/O. Do not put real held-out labels on the host filesystem accessible to worker. No real-data benchmark is allowed until stronger independent isolation, per-request write deadlines, process-group cleanup, threat-model review and frozen protocol are implemented and tested.

Upload all four code/workflow files (plus this document) into the named paths on `bhs-scientific-audit`; do not merge to `main` or mint a Zenodo release. Run `BHS Synthetic Process Oracle Deadline Gate` in Actions and inspect logs before advancing.
