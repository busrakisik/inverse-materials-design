# BHS v12.4 — Completion-matched decisions and abstention audit

**Pre-outcome development protocol, 7 November 2026.** This file is committed before any new v12.4 scored campaign. All source outcomes will be manufactured; original historical and physical archives are excluded.

## Research question

Under a matched 48-response budget, can a completion-constrained version of the frozen v12 evidence gate improve *decision reliability*, not simply acquisition count? Compare against frozen GP–ARD, GP pooled-noise EI, GP pooled-noise IVR and random bundled methods. Include the unmodified gate as a **diagnostic arm**, not a matched comparator. Preserve negative outcomes regardless of direction; no model weights, thresholds, seeds, acquisition scores or study sources may be changed after reviewing results and described as confirmatory.

## Fixed paired source design (evaluator-only)

- Exactly **48 distinct public four-coordinate designs**: NumPy `default_rng(48121).uniform(-1,1,(48,4))`.
- Two latent landscapes, hidden from selectors, where `x0..x3` denote columns:
  - `ridge`: `3 + 1.4*exp(-6*(x0-0.35)**2) + 0.9*x1 - 0.6*x2**2 + 0.5*x0*x3`.
  - `oscillatory`: `3 + 1.1*sin(2.5*pi*x0)*cos(1.5*pi*x1) + 0.7*x2*x3 - 0.4*x1**2`.
- A single independent manufactured standard-normal `48-by-3` table drawn from `default_rng(79331)` is fixed *before* any policy or order selection; reuse it across paired methods and regimes.
- Two observation-noise regimes: `constant` uses standard deviation `0.35`; `varying` uses `0.15 + 0.55*(x0+1)/2`. The design-dependent noise levels are evaluator-only.
- Decision seeds **(19, 29)**; replicate-order variants **(0, 1)**, with a deterministic independent per-design permutation `SeedSequence([48121, seed, variant, geometry_id])`. These are manufactured *development* settings, not independent physical holdouts.
- Fixed design/noise reference versions: NumPy 1.26.4, SciPy 1.13.1, scikit-learn 1.5.2, pandas 2.2.3, Python 3.11.

## Fixed policy arms and completion rule

All methods receive the same six completely measured initial designs (18 outcomes), exactly one new response per later action, and stop after **48 total responses**. Each geometry has at most three possible responses. At most three partly measured designs may remain open during allocation. Every policy receives public descriptors and already revealed values only.

Comparison arms (six): `random_bundled`, `gp_ard_bundled`, `gp_pooled_noise_ivr`, `gp_pooled_noise_ei`, `evidence_gate_native`, and `evidence_gate_completion`. The native arm delegates directly to the existing frozen v12.1 gate; other inherited selectors remain unchanged. The matched completion arm first obtains the *unchanged* gate's proposed action, then applies the shared feasibility rule; it does not modify GP models, fitted likelihoods, EI/IVR scores or gate thresholds.

The **same completion-feasibility wrapper** is applied to all five matched comparison arms. Let `R` be responses remaining including this action; let `O = sum(3 - n_i)` over existing partially measured designs. A new design may be started only if `R >= O + 3` and fewer than three partial designs are open. Actions on existing partial designs must be the next ordinal and remain eligible. If a proposal is infeasible, deterministically complete the pending design needing the fewest further responses, then prefer higher currently observed mean, then smaller geometry ID. This is a feasibility filter, **not** a demonstrated optimal stopping or value-of-information rule. The unmatched native gate is reported separately to expose completion waste.

No policy is trained or tuned on the latent function. Because inherited methods use different internal acquisition scores and GP noise assumptions, even matched completion eligibility does not isolate the causal value of repetition.

## Frozen evaluator and decision loss

After exactly 48 valid reveals, recommend the *fully measured* geometry with the greatest observed triplicate mean, with lowest-ID ties. Latent qualities and the latent pool optimum remain evaluator-only. Partially observed designs are not eligible for final recommendation.

Use a **common, policy-neutral evidence sufficiency filter** on all six arms. From only completed triplicates, obtain the two highest observed means; let `d` be their difference. Estimate a shared within-completed-geometry response variance using pooled residual sum of squares divided by the total within-design degrees of freedom. The standard error of the top-two mean difference is `sqrt(2*pooled_variance/3)`. The recommendation is accepted iff `d > z*SE`; otherwise abstain. This is a heuristic *not* a calibrated probability of correct recommendation and does not prove safety.

**Primary endpoint:** mean abstention-adjusted loss at `z=1.0`, abstention penalty `0.50` in manufactured latent-quality units. Loss equals evaluator-only latent simple regret of the recommended design if accepted; otherwise `0.50`. Lower is better.

Predeclared diagnostic thresholds `z=(0,1.0,1.645)` and abstention penalties `(0.25,0.50,1.0)` form a descriptive coverage–loss grid; none can replace the primary endpoint post hoc. Also report:
1. Accepted-decision coverage and *conditional* regret, never suppressing low-coverage policies.
2. Raw recommendation latent regret and best completed-design latent regret (oracle-only diagnostics).
3. Number of completed designs, unfinished designs, and responses stranded in unfinished designs.
4. Per-seed/order/regime paired differences, order sensitivity, and the number of feasibility interventions; benchmark entire campaigns at identical response counts.
5. Verification of source/implementation/outputs with exact SHA-256 or Git hashes and all negative outcomes. Do **not** present two seeds and two orders as independent statistical replication.

No significance tests, intervals, calibrated clinical/physical risk claims, demonstrated laboratory savings, or generalized superiority are permitted. Any ties or differing coverage remain visible.

## Execution gates

- Commit this protocol first. Implement a separate evaluator with strict use-once measurement ledger, forbidden reserved seeds `10000..10099`, and byte-consistent outcome construction.
- Verify every policy sees only descriptors and previously revealed outcomes. Changing future unseen responses cannot change the next acquisition.
- Run source-independent unit tests in CI; do not automatically execute the scored study on push.
- An explicit source-independent execution must retain all 96 campaigns (2 landscapes × 2 regimes × 2 seeds × 2 orders × 6 methods), regardless of direction. If a gate fails, archive but mark the results **invalid**, never successful.
- Original V11 negative study and first V12 historical replay failure are immutable. Existing V12.3 outcomes are prior exploratory evidence. Future use of actual physical data requires an untouched prospective source with true timestamps, batches, equipment logs, uncertainty and domain-expert review.

## Evidence boundary

`development_only=true`; `scored_validation_allowed=false`; `independent_holdout_used=false`; `physical_validation_by_bhs=false`; `causal_identification=false`; `calibrated_uncertainty_proven=false`; `claim_of_superiority=false`; `real_savings_measured=false`; `reserved_nist_seeds_used=false`.

