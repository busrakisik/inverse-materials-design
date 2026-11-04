# BHS Label Boundary Audit v1

**Status: STATIC REVIEW ONLY — NOT AN INDEPENDENT LABEL FIREWALL.**

## Purpose

Make the distinction explicit between normal policy-interface behavior and enforceable isolation. This stage does not score held-out tasks, access held-out labels, or issue validation approval.

## Findings based on current synthetic code

1. `MeteredEvaluator.run` normally sends public descriptors and previously observed values to `policy.choose`.
2. `SyntheticTask` holds hidden utilities as a Python `_labels` mapping.
3. The trusted evaluator accesses this mapping to obtain selected outcomes.
4. The exploratory pilot accesses the same mapping to calculate regret after evaluation.
5. Policy calls execute in the same Python process as the trusted evaluator. Python's `_labels` naming convention does **not** enforce confidentiality. A malicious policy could potentially introspect call frames or other objects.

These findings do not establish leakage in the ordinary `BayesianOnlyPolicyV1`; they establish that an **adversarial policy isolation claim is unsupported**. An honest policy receiving only public arguments is a weaker guarantee than a protected held-out evaluator.

## What this package does

- Adds 8 label-boundary contract tests and runs the previously unexecuted 8 artifact redirect tests in CI, alongside the original 10 reconciliation tests: 26 tests total across three suites.
- Re-runs the five pinned ZIP artifact checks.
- Emits a hashed static risk report.
- Always reports `scored_validation_allowed: false` and `adversarial_code_isolation_established: false`.

## Important limitations and next scientific steps

- AST inspection is not a process-isolation penetration test.
- A robust boundary must execute an untrusted policy outside the trusted evaluator process, pass only serialized public descriptors and prior observations, and reject attempts at arbitrary filesystem/network access or code execution as appropriate for the threat model.
- Even a working process boundary is not sufficient to authorize independent validation: historical seed audit, frozen analysis plan, immutable environment provenance and independent review remain outstanding.
- Do not run holdout seeds 10000–10099 at this stage.
