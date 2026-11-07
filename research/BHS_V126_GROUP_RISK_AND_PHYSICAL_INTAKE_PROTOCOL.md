# BHS v12.6 — Group-risk audit and prospective physical-source intake

**7 November 2026. Scope: post-result methodological audit, not a new predictive evaluation or a pre-results registration of V12.5.**

## Immutable reference and objective

The V12.5 calibration and evaluation campaigns, thresholds and outputs already exist and have been inspected. The original calibration and evaluation archives are read-only. No new scores, calibration thresholds, acquisition parameters or historical selections will be changed. This follow-up tests the *interpretation* of the reported decision-risk evidence and defines a structural intake contract for genuinely prospective measurements.

Original archives on `bhs-v125-evidence-archive`:
- Calibration JSON SHA-256 `fe47b0f79d04ff45df39498559d59dbfc941796c2d195dec4b1cfa4e406cfd48`.
- Evaluation JSON SHA-256 `654def586730c51793cf4040752770349a25dbcd4c808da86469a5f649e7b831`.
- V12.5 source blob `fa5419b0a65b7b83fafe214d2c18b9df4f0e04e7`.
- V12.5 protocol blob `719431338ee9cd0b3ecc50d197b946aeb79c4701`.

## Group dependence rule — fixed audit, not retuning

- Six inherited methods; `0.50` calibration coverage cap only, using the **unchanged frozen thresholds**. No new threshold is fit.
- Exactly 4 calibration groups and 4 disjoint evaluation groups; each group has two **dependent** measurement-order variants for each method. Campaign-level accepted/error counts remain descriptive.
- For each method, a group is **covered** if at least one of its two order variants is accepted. A covered group has a **failure** if *any* accepted variant has evaluator-only regret above `0.35`. This is a conservative **group-level union event**, not an inference about independent errors within one group.
- Report 8 evaluated decisions, accepted decision count, 4 evaluated groups, accepted group count, group failure count, a zero-coverage flag and group-level empirical failure fraction. Missing or duplicated group/variant/method cells are fatal.
- As a **sensitivity illustration only**, compute the one-sided 95% Clopper–Pearson upper binomial bound `beta.ppf(0.95, failures+1, accepted_groups-failures)` for `0 <= failures < accepted_groups`; if all accepted groups fail use `1`, if none are accepted use `null`.
- The interval requires independent identically distributed Bernoulli group outcomes and appropriate threshold/selection conditions. Neither physical independence nor population exchangeability is established for these manufactured, related groups. Therefore the numeric bound **cannot be advertised as physical, distribution-free or validated control**.
- A hypothetical zero-failure 95% upper bound below or equal to `0.25` needs at least **11 independent groups**, not four. This is a minimum illustration and not a complete power analysis or permission to deploy.
- Evidence gate: `physical_recommendation_allowed=false`, `independent_validation_established=false`, `statistical_guarantee_supported=false` for every policy, even if the numerical upper bound were small.

## Integrity requirements

- Verify the exact original bytes and SHA-256 of both archived JSON reports; validate their internal split labels and per-row digests.
- Check that the calibration/evaluation source groups do not overlap. All 2-by-6 records within a group must share the same original source fingerprint.
- Require 48 evaluation responses per campaign, finite nonnegative latent regret, a Boolean high-regret flag matching the frozen `0.35` boundary, and no future outcomes exposed to selectors.
- Verify that the frozen evaluation thresholds match the calibration document. Reject fabricated omissions, duplicates, forged errors and changed thresholds.
- Read archives **without retrieving the physical historical source**. No manufactured reruns or fresh fitted thresholds in CI.

## Prospective physical intake: structural acceptance only

An immutable original JSON byte payload, independently supplied to a future investigator, must be checked against a declared SHA-256 and source/license/units. Every measurement record requires: a unique measurement event identifier, group, design and replicate identifier, time with explicit timezone, apparatus identity and calibration reference, synthesis batch, measurement batch, finite response and positive uncertainty, acquisition duration and cost, and an explicit `calibration` or `evaluation` partition.

- Reject duplicate events or replicate identities, missing/out-of-order replicate ordinals, nonmonotone replicate timestamps, nonfinite results, nonpositive uncertainty/cost/duration and unknown groups.
- Reject any geometry, synthesis batch or measurement batch appearing in **both partitions**; matched split units are broader than one measurement event.
- Require a nonempty investigator approval reference and source license, but **do not infer that the references are authentic or that equipment is scientifically calibrated** from the presence of strings.
- Treat an original byte checksum match as technical integrity only, not measurement accuracy or independent provenance.
- Structural success still returns `physical_recommendation_allowed=false`. Authentic signatures, data ownership, real safety verification and independent evidence require external human review.

This repository will contain **only manufactured structural test fixtures**, never unidentified personal records, unlicensed physical laboratory data or automated experiment commands.

## Negative/conditional evidence

Past V11 negative results, first failed V12 historical parity replay, V12.3, V12.4 and V12.5 mixed results remain unchanged. Existing old release tags are not rewritten. Reserved seeds `10000..10099` are untouched. The V12.6 module generates **no new physical or manufactured performance observations**.

Prior statistical method: Clopper and Pearson (1934), *Biometrika*, DOI 10.1093/biomet/26.4.404. Selective inference can require safeguards beyond unconditional binomial intervals; this simple post hoc sensitivity diagnostic is not a substitute for selective-risk theory.

## Hard gates

`development_only=true`  
`scored_validation_allowed=false`  
`independent_holdout_used=false`  
`physical_validation_by_bhs=false`  
`causal_identification=false`  
`calibrated_uncertainty_proven=false`  
`claim_of_superiority=false`  
`real_savings_measured=false`  
`reserved_nist_seeds_used=false`

