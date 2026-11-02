# BHS synthetic oracle / policy interface — contract v1

**Status: SYNTHETIC_CONTRACT_ONLY / REAL_LABEL_FIREWALL_NOT_IMPLEMENTED / NO_BENCHMARK_RUN.**

- `ControlledOracle` receives a trusted in-memory mapping of fabricated labels; the selection callback receives only a frozen `PublicView` of candidate IDs, remaining budget and previously queried `Observation` entries.
- Each distinct query consumes one unit; unknown IDs, re-queries, budget overflow, invalid budgets and non-finite values fail closed.
- `run_synthetic_trial` stores *only candidate IDs and step numbers* in its report; no synthetic label values are published by this report.
- This is an **API contract**, not a security perimeter: the oracle's underlying labels are held in the same Python interpreter. A hostile callback could use introspection or external shared state to find them. Avoid claiming adversarial isolation from these tests.
- **Before touching real test labels**: move the private oracle to an isolated subprocess/service with allowlisted request/response schemas, deny policy process direct access to raw data or file paths, and test attempted bypasses. Only allow validation and training labels for fitting before the held-out evaluation.
- The scientific objective remains a proposal: 1.5 eV target, K=10, five held-out evaluation pools, baseline choices pending independent rationale and validation-only work.
- Matbench source-data redistribution and attribution review remains open. Do not commit or ship real raw dataset labels or publish their values in CI artifacts.
- No empirical BHS advantage, discovery, stability, DFT, or CHGNet performance is implied by these contract tests.

## Next gate
Upload module, tests, and this protocol to `bhs-scientific-audit`. Run isolated synthetic contract tests on GitHub only after file paths have been checked; later add a separate manual-only CI workflow. Do not enable a real dataset oracle yet.
