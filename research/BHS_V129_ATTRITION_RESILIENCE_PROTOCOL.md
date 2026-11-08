# BHS v12.9 — Design attrition, session resilience and independent-unit accounting

**Prepared 8 November 2026.** This is a post-v12.8 **development design audit**, not prospective experiment registration, a power analysis, new physical measurement or validation of a materials mechanism. V12.8's 8-coupon saturated design and original no-go record remain intact.

## Frozen structural question

For a provisional Fe–Co–Ni magnetic thin-film pilot, can a proposed *within-synthesis-batch* reference-versus-modified coupon contrast remain mathematically estimable when one whole synthesis batch or measurement session becomes unavailable? Can a seemingly improved design still be rejected for unavailable physical measurement precision, sample-size evidence, material rights or actual independent batch provenance?

**Critical conditional premise:** Coupon-level assignment to two processing arms within a synthesis batch has not been confirmed physically possible by a collaborator. If the treatment is necessarily applied to an entire synthesis batch, both illustrations are inapplicable, and the randomized/experimental unit and rank model must be redesigned by the laboratory.

## Two outcome-free, development-only fixtures

A: `cross_session_pairs`: eight artificial synthesis batches B01–B08, each with exactly one reference and one modified coupon, deliberately distributed across two MOKE sessions S1 and S2. Session slots 1–8 contain four of each arm, with equal mean position. Batch IDs, arm labels, session and assigned slot are fixed by `research/BHS_V129_DESIGN_VARIANTS.json`.

B: `within_session_pairs`: the same eight artificial synthesis batches and 16 coupon counts, but each batch's reference and modified coupons belong to the **same** session. Batches B01–B04 belong to S1; B05–B08 to S2. Both sessions have four coupons per arm and equal mean slot positions. The alternative preserves treatment balance when one whole measurement session disappears, but may be operationally infeasible depending on whether the lab can process and measure both arms in each batch/session.

These are **not** claims about optimal sample size, feasible throughput, guaranteed randomization, batch independence, genuine effect sizes, or physical cost. Each coupon declares three intended technical magnetic traces; the 48 traces are not 48 independent samples. Structural diffraction is planned but no scans or outcomes exist.

## Predeclared outcome-free diagnostics

Use the frozen V12.8 rational linear-algebra function for all designs, without fitting magnetic responses. For each fixture and each deletion scenario:

- Form the declared nuisance matrix: intercept, synthesis-batch fixed effects (one reference level omitted), session fixed effects (one omitted), session-specific centered linear measurement position. Add one binary processing indicator.
- Report the exact nuisance rank, full-model rank, residual row degrees of freedom, whether treatment is linearly estimable (rank increment), unique surviving batches, unique surviving sessions, coupon count and technical-trace count.
- Full-plan and leave-one-*batch* diagnostics must be computed for all eight batches. A *single-session loss* must be audited for S1 and S2, even when the surviving design has only one session.
- Structural robustness condition requires `treatment_estimable=true` and `residual_degrees_of_freedom>0`; it never means causal validity, adequate precision, or safe execution. Return individual deletion results and count failures without selecting favorable scenarios.
- Retain a sentinel failure check for the unchanged V12.8 eight-coupon design: `residual_degrees_of_freedom=0`. Technical trace multipliers cannot change coupon-level design rank or independent batch count.
- Review session-level balance and the cross-batch dependence from shared fabrication; if any group or session has only one arm, record the limitation separately.
- Require no response/outcome or researcher-approval claims in fixtures. Every report includes `physical_recommendation_allowed=false`, `laboratory_action_allowed=false`, `statistical_guarantee_supported=false` and `independent_physical_validation_established=false`.

The rank calculation is **conditional on a linear additive nuisance model**. Its residual degrees of freedom are algebraic coupon-row counts, not degrees of freedom for valid cluster-robust uncertainty with a small number of batches. It does not estimate intraclass correlation or evaluate laboratory costs. Session and batch fixed effects may be aliased when sessions are nested in batches; this is captured by rank and must not be interpreted as independently estimable main effects.

## Failure-focused tests

1. Reject unexpected fields, response values, modified physical approval flags and altered original v12.8 source identities.
2. The original eight-coupon fixture must remain saturated; no inflation by repeated technical traces.
3. Both new fixtures must have 16 coupons and eight **named** batches, exact within-batch treatment pairing, and balanced measurement-session arms/positions.
4. One-batch removal must not be mistaken for a new prospective data source. Preserve and disclose every rank/degree-of-freedom result.
5. One-session loss is a genuine structural stress test: cross-session pairs lose one arm from every surviving batch and become treatment-confounded, while within-session pairs retain paired coupons in the surviving four batches.
6. Negative missing-sample, duplicated coupon, duplicate slot, no-XRD and physical-release claims fail closed.
7. Changing the count of technical traces never changes the independent unit, rank, degrees of freedom or deletion-resilience outcomes.

## Beyond a computational fixture

Actual preparation, processing, MOKE/XRD settings, verified film thickness/composition, independently characterized instrument calibration, sample loss rates, uncertainty in A/m, minimum meaningful effect, genuine batch independence, economic/measurement costs, study population and independent prospective partition all require a qualified materials investigator. The number of batches needed for a reliable group-level inference **cannot be calculated from these no-outcome fixtures**. A collaborator must justify a prospective sampling and randomization strategy, verify that the proposed treatment unit is physically assignable and approve all safety/rights requirements.

All V11–V12.8 nonpassing and mixed original evidence stays unmodified. No physical operations occur. The reserved seed range 10000–10099 remains unused. Published versions and Zenodo provenance are not rewritten.

Scientific background: estimating uncertainty under grouped observations generally requires accounting for intragroup correlation, not counting technical responses as independent: <https://academic.oup.com/ije/article/52/5/1648/7172835>. That cluster-randomization review is methodological context, **not** proof that this unapproved coupon-level arrangement is a cluster-randomized experiment.

**Gates:** `development_only=true`; `scored_validation_allowed=false`; `physical_validation_by_bhs=false`; `independent_holdout_used=false`; `physical_recommendation_allowed=false`; `laboratory_action_allowed=false`; `statistical_guarantee_supported=false`; `claim_of_superiority=false`.

