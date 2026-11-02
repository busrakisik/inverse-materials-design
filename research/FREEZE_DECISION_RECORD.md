# BHS Independent Synthetic Validation — Freeze Decision Record v1

**Status:** DRAFT / NOT_FROZEN / HOLDOUT_NOT_RUN / NO_PHYSICAL_CLAIMS  
**Prepared:** 2026-11-02

## Verified preparation milestone
GitHub Actions run `41466830970` concluded success, with seven tests passing. Its source commit was `bd42bb437ccf3521910c0453897ebf0a5f31e6bf`. This is evidence that the metadata preparation workflow executed; it is **not** evidence of independent experimental validation.

## Existing synthetic pilot
The exploratory pilot used 30 task seeds (0–29), five scenarios, budgets 1/2/5/10, and three policies (random-without-replacement, descriptor greedy, Bayesian-only). Its outcomes have already been inspected. All decisions informed by these outcomes must be labeled **pilot-informed**; this does not invalidate an independently frozen, untouched validation set, but must be disclosed.

## Proposed holdout, not yet approved
- Candidate seeds: 10000–10099 inclusive; **proposed only**.
- Disjoint from documented 0–29 pilot seeds; not yet audited against *all* previous development experiments.
- Must archive the literal seed list and SHA-256 *before* running any held-out evaluation.
- Do not inspect hidden outcomes for these seeds until the freeze is approved.

## Policy/model specification to verify and freeze
- `BayesianOnlyPolicyV1`: scalar-feature Gaussian linear regression with `prior_variance=1.0`, `noise_variance=0.1`, `exploration_scale=1.0`; seeded Thompson-like coefficient sampling. Confirm code values and no later tuning.
- `UniformWithoutReplacement`: seeded random baseline.
- `DescriptorGreedy`: highest public descriptor, deterministic tie-breaking.
- Twenty candidates per scenario, maximize best observed utility, budgets 1/2/5/10.
- Policy RNG seed is deterministically derived from task seed/scenario/policy in existing pilot runner. Record the exact implementation and version before the next run.

## Decisions required BEFORE frozen evaluation
- [ ] Audit every prior tuning/development seed; demonstrate disjointness from 10000–10099.
- [ ] Predeclare **one primary scenario** and rationale. If pilot-informed, state this explicitly. All other scenario/budget contrasts remain exploratory.
- [ ] Select and freeze policy parameter values and tie-breaking rules.
- [ ] Freeze generator, evaluator, policy, baseline, runner, and analysis source commit SHA and checksums.
- [ ] Record locked Python/dependency environment and hash.
- [ ] Record paired bootstrap procedure, bootstrap RNG seed, and handling of missing/invalid runs.
- [ ] Complete independent public-descriptor/hidden-label access audit.
- [ ] Store one machine-readable, immutable freeze manifest and a reviewable approval before executing.

## Predeclared primary contrast template
`mean(best_utility_bayesian_only(B=10) - best_utility_random(B=10))` on paired task seeds for the **declared primary scenario**, with 10,000 paired bootstrap resamples and a 95% percentile interval. Claim scope: *synthetic benchmark only*. No material-property or physical superiority claim.

## Release decision
**NOT APPROVED TO RUN HOLDOUT.** The seven green preparation tests do not fill the checklist above. Continue with freeze audit and manifest finalization; run evaluation only after all gates have independent evidence.
