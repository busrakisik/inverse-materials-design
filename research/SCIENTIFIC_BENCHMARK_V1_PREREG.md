# BHS Scientific Benchmark v1 — preregistration draft

**Status: DRAFT / SYNTHETIC-FIRST / NOT_RUN / NO_HELD_OUT_TEST_ACCESS / NO PERFORMANCE CLAIMS**

## Question and estimand
Does a genuinely implemented, explicitly specified hypothesis-centric selection policy achieve higher best-observed utility than budget-matched baselines, on synthetic evaluation tasks with identical information access? All claims are limited to this synthetic setting until independently evaluated on a frozen real-data protocol.

## Pre-experiment gates (must pass before any scored run)
1. Freeze a revision SHA, environment lock, input-data hash, synthetic generator spec, and baseline implementations. Record any changes as a new version, not an amendment after seeing results.
2. Verify policy code really implements the stated algorithm; distinguish Bayesian updating, greedy acquisition, and MCTS/PUCT. A first-unqueried-ID worker is **not** BHS.
3. Define and run leakage tests: hidden values never supplied to policies except previously queried outcomes; split construction never uses labels.
4. Fix baseline budgets, seeds, direction of utility, tie-breaking and hyperparameters solely using development data.
5. Document license and provenance for any later real dataset. Do not load real held-out labels into an accessible worker filesystem.

## Experimental unit
A generated synthetic candidate pool per (scenario, seed), with ground-truth utility available only to the trusted evaluator. Policies receive candidate IDs and permitted *public* descriptors plus outcomes of their own previous queries. Each policy gets the same pool and query budget.

## Synthetic scenarios
- Smooth correlated utilities, with informative public descriptors.
- Multimodal utilities, with deceptive local optima.
- Uninformative public descriptors (negative control).
- Mismatched or noisy evidence likelihoods (stress test).
- Duplicate-like public descriptors, ensuring query identity and no repeated evaluations.

Scenarios must not be tuned after inspecting holdout outcomes. No simulated result can establish accuracy on physical materials.

## Baselines and BHS variants
- Seeded uniform random without replacement.
- Fixed descriptor-based greedy heuristic (declared before evaluation).
- Uncertainty sampling only when a fitted uncertainty estimator with identical training access is implemented; otherwise mark NOT_IMPLEMENTED, not a passing baseline.
- BHS Bayesian-only and BHS + MCTS/PUCT, only if independently verified as implemented; otherwise mark NOT_IMPLEMENTED. No renaming toy workers as BHS.

## Budgets and repetition
Predeclare budgets 1, 2, 5, 10 (only if pool has at least 10 candidates); use at least 30 paired seeds/scenario for exploratory runs. Seeds are fixed before any scored run and must be distinct from policy-tuning seeds. Report total oracle calls, wall time, and computational resources.

## Primary and secondary metrics
Primary: best utility observed by each policy by budget B, evaluated with the same orientation. Primary contrast: paired difference BHS minus seeded random at B=10 on a preselected primary scenario. If BHS is unimplemented, NO PRIMARY CONTRAST IS RUN.
Secondary: simple regret relative to pool optimum (computed evaluator-side only), area under best-observed-utility curve, time, query count and invalid actions. Show uncertainty intervals per scenario/budget; no pooling across incompatible utility scales.

## Analysis
Report per-seed paired differences, mean/median, bootstrap 95% intervals (seed-paired resampling), and full distribution. Treat additional scenarios and budget comparisons as exploratory, label multiple comparisons; no superiority claim based solely on positive point estimates or single seed. Archive raw logs and failures. Provide negative controls and ablation results.

## Stop / fail conditions
Abort scored evaluation on any leak, duplicated query, budget mismatch, non-finite outputs, missing provenance, or implementation mismatch. An oracle/sandbox gate success does not satisfy algorithmic validation. Synthetic scores must be marked SYNTHETIC_ONLY.

## Sequence
A. Audit existing benchmark and policy code. B. Add deterministic generator + reference baselines + strict evaluator contracts. C. Verify deterministic synthetic runs and inspect negative controls. D. Implement genuine BHS policies. E. Freeze protocols, conduct paired evaluations. F. Independently evaluate externally governed real-world data after permissions and isolation review.

## Provenance table (to be filled before run)
Commit SHA: TBD
Python and dependency lock: TBD
Generator version/hash: TBD
Policy versions: TBD
Baseline versions: TBD
Seeds file/hash: TBD
Task specification checksum: TBD
Date preregistration frozen: TBD

**Interpretation:** This is a protocol draft only; no trials or scores were produced by writing it.
