# BHS v12.3 — Controlled synthetic measurement-order protocol

**Status (7 November 2026): frozen before v12.3 outcome scoring.** Only manufactured observations are used. The previously inspected historical physical dataset is excluded.

## Falsifiable objective

Under the same 48 individual-response acquisition budget, compare the frozen V12 evidence gate and bundled methods against V12.2 adaptive GP references. Examine how the response reveal order changes the final recommended design. These are manufactured development cases: a favorable outcome cannot establish independent scientific validity or laboratory savings.

## Fixed experiment specification

- Exactly 48 candidate geometries with 4 public descriptor coordinates from NumPy `default_rng(20261107).uniform(-1,1,(48,4))`.
- Evaluator-only latent quality: `4 + 1.8*sin(1.4*pi*x0) + 0.9*x1**2 - 0.7*x2 + 0.5*x0*x3`.
- Exactly three fixed noisy observations per candidate: one independent 48-by-3 standard-normal table from `default_rng(73123)`.
- Two frozen regimes: `constant` with response standard deviation `0.35` and `varying` with geometry-dependent standard deviation `0.15+0.60*(x0+1)/2`. The same normal-noise table is used for both.
- Decision seeds `(7,13)`; observation-order variants `(0,1)`; each geometry's three outcomes are permuted by `default_rng(SeedSequence([20261107,seed,variant,geometry_id]))` independently of selection decisions.
- Five frozen policies: `random_bundled`, `gp_ard_bundled`, `evidence_gate_development`, `gp_pooled_noise_ivr`, `gp_pooled_noise_ei`. The first three invoke the frozen V12.1 canonical selector; the latter two invoke the frozen V12.2 selector. All model settings remain unchanged.

## Acquisition and evaluation

Each campaign shares the same six fully measured starting geometries (18 observations). Every later action reveals exactly one response until 48 total observations have been acquired. Hidden results, the geometry-dependent noise values, true latent responses, full oracle tables, and the latent optimum are evaluator-only. An ordinal gap, repeated read, budget overrun or forged transcript invalidates the experiment.

The recommended geometry is the fully measured design with the largest observed triplicate mean, tie-broken by lowest geometry ID. Partially measured designs are ineligible for recommendation.

**Primary metric:** evaluator-only latent simple regret = best latent quality in all 48 candidates minus latent quality of the recommended completed design. **Secondary diagnostics:** best fully measured latent-quality regret, completed and partial design counts, matched 48-response budget, and per-seed, per-order sensitivity. Preserve individual campaign values and aggregate descriptive means. No statistical significance, confidence intervals, generalized superiority or causal attribution is permitted.

## Mandatory contract gates

1. The synthetic source is deterministic; all reveal-order variants preserve each design's outcome multiset.
2. All policies share the same pool, initial designs, latent quality function and hidden noise table, at identical measurement budgets.
3. The oracle has a private, one-use measurement ledger. Policies receive only descriptors, already observed responses, seed and step.
4. Counterfactual changes to unseen outcomes cannot alter the immediate acquisition decision.
5. Protected seeds `10000..10099` remain unused. Existing V12, V12.1 and V12.2 tests still pass.
6. CI runs source-independent contracts only. A full synthetic result run is a separate explicit command, with no historical physical-source retrieval.

## Limitations and prior work

The fixed pool has only three potential observations per geometry. The changing-noise regime tests model misspecification: V12.2 uses a shared estimated noise variance. Completion rules differ among policies; result differences cannot isolate the effect of repeating measurements. Replication/exploration methods and heteroscedastic Gaussian-process models are established prior art: Binois et al., *Technometrics* (2019), DOI 10.1080/00401706.2018.1469433; Binois and Gramacy, *J. Statistical Software* (2021), DOI 10.18637/jss.v098.i13.

The original V11 negative finding and V12 non-passing physical-source replay remain preserved without alteration.

## Evidence boundaries

`development_only=true`; `scored_validation_allowed=false`; `independent_holdout_used=false`; `physical_validation_by_bhs=false`; `causal_identification=false`; `calibrated_uncertainty_proven=false`; `claim_of_superiority=false`; `real_savings_measured=false`; `reserved_nist_seeds_used=false`.
