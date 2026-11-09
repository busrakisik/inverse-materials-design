# BHS v12.12 — Outcome-free paired-contrast variance sensitivity

**Protocol frozen before computing the first v12.12 report. 9 November 2026.**

## Purpose and inference boundary

V12.8–V12.10 identify algebraic estimability and different physical treatment-assignment units. They do not establish the precision of the resulting treatment contrast. This study provides **symbolic, conditional variance decomposition** for the existing manufactured schedules. It neither estimates actual material variability nor provides sample size, power, calibration, causal identification, magnetic outcomes, approved laboratory instructions or an empirical BHS advantage. Current physical decision remains **NO-GO**.

The primary contrast is the mean of complete matched-block differences, modified minus reference, measured in A/m. Each matched block has one coupon per arm. Weights are +1/B for modified and -1/B for reference where B is the number of surviving complete pairs. Other coupons are excluded from this paired contrast. This is a diagnostic linear estimand, not the adjusted regression estimand studied in V12.8–V12.10; an observed regression estimator may have different precision.

## Fixed inputs and provenance

Read only these frozen schedules from the v12.11 evidence archive, with exact SHA-256 validation:

- `research/BHS_V129_DESIGN_VARIANTS.json`: `e65e85a6c2d1a8fed749fdd3502c9021343ca53bb01fb0ec06306101961abde6`
- `research/BHS_V1210_ASSIGNMENT_UNIT_FIXTURES.json`: `adc920e2eba62c7e86ad93b227a0327c692952e0bbb2036907c38326974a5a42`

No outcomes are read. Do not modify previous reports, source artifacts or original first-run data. These layouts have not been approved by an external laboratory.

## Explicit hypothetical stochastic model

Assume an additive, exchangeable, zero-mean, mutually independent random-intercept model, conditional on the schedule: each *source deposition run* contributes an offset of variance `sigma_run^2`; each *MOKE session* an offset of variance `sigma_session^2`; each *coupon* an offset of variance `sigma_coupon^2`; each planned technical MOKE trace contributes independent measurement variance `sigma_trace^2`, averaged within coupon. All variances are in (A/m)^2. V12.9 `synthesis_batch_id` stands in for a source run for sensitivity only and V12.10 uses `source_deposition_run_id`. There is no additional batch/block random intercept, no separate process-event component, no verified independence and no spatial/temporal bias model. A shared intervention would require revising the model. This restrictive model is **not** a physical finding.

For weights `w_i`, source groups `g`, and `m_i` traces per coupon:

`Var(Dbar) = C_run*sigma_run^2 + C_session*sigma_session^2 + C_coupon*sigma_coupon^2 + C_trace*sigma_trace^2`

where `C_run = sum_g (sum_{i in g} w_i)^2`, `C_session` is analogous, `C_coupon = sum_i w_i^2`, and `C_trace = sum_i w_i^2/m_i`. Fractions are exact. Report all four coefficients, including zero values. The result is a *model-based marginal variance*, not an independent-group robust estimate, valid confidence interval or a sampling model learned from records.

## Frozen comparison set and diagnostics

For all four schedules (V12.9 cross-session, within-session; V12.10 postdeposition coupon, deposition-run), compute complete schedule, deletion of each one source deposition run, deletion of each one MOKE session, and deletion of each one matched pair. Output the coefficient range across all deletions, the number of complete pairs, and `NOT_ESTIMABLE` when fewer than two complete pairs survive. Do not cherry-pick a favorable loss scenario. The two-pair minimum is a descriptive diagnostic; it does not certify inferential degrees of freedom or robust risk bounds.

For an illustrative dimensionless sensitivity grid set `sigma_coupon=1`, `sigma_trace=1`, `sigma_run` in `{0,1,2}` and `sigma_session` in `{0,1,2}`. This scale is an arbitrary unit equal to one hypothetical coupon standard deviation; it is **not an observed A/m value**. Compare symbolic standard errors for the two V12.10 treatment scopes under equal ratios, but do not compare cost efficiency without measured run and measurement costs.

The first testable deductions under these assumptions are: V12.10 coupon-level postdeposition pairs cancel a *shared source-run* offset, whereas the deposition-run comparison does not; three technical traces reduce only their technical-error component; full-schedule session balance does not imply resistance to missing sessions. A difference under an alternative covariance model must be reported rather than concealed.

## Falsification and required next evidence

1. Reject duplicate coupon identity, incomplete paired-group definitions, invalid planned-trace counts and mismatched source hashes. Outputs must be independent of row ordering and arbitrary renaming of identifiers.
2. Show within-pair shared-run cancellation by exact algebra, and expose the extra run component for separate deposition runs; test against independent hand calculations.
3. Preserve all missing-session cases, including those with no complete pair; report *no estimate* instead of zero variance or spurious confidence.
4. Reject converting manufactured ratios into empirical noise estimates, physical treatment effect, resource savings, or a selected sample size.
5. External investigator must first verify actual physical treatment unit, real independent manufacturing runs, MOKE session chronology, composition/thickness, field calibration, source rights, meaningful effect and observed covariance structure. Until then retain `development_only=true`, `scored_validation_allowed=false`, `independent_holdout_used=false`, `physical_validation_by_bhs=false`, `formal_power_or_precision_established=false`, `claim_of_superiority=false`, `real_savings_measured=false`, `physical_recommendation_allowed=false`, `laboratory_action_allowed=false`.

The protected historical NIST seed range `10000..10099`, original negative comparisons, old tags and public default branch remain untouched.
