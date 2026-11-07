# BHS v12.8 — Fe–Co–Ni prospective design estimability contract

**7 November 2026. Pre-outcome structural design review only.** The demonstration plan contains manufactured identifiers and no physical measurements. This protocol does not authorize fabrication, instrument use, outcome scoring, laboratory recommendations or physical performance claims.

## Why this step is necessary

V12.7 identified 27 unresolved pilot conditions. A new independent experiment cannot simply choose two processing settings and count repeated instrument traces as independent successes. If all reference coupons are prepared in one batch and all modified coupons in another, the processing contrast is confounded with batch. If measurement sessions systematically separate treatments, the contrast can be confounded with instrument/session drift. Computing more model posteriors cannot fix a non-identifiable experimental design.

The candidate physical question remains provisional: Fe–Co–Ni thin films, a lab-approved processing contrast, coercive field in A/m from verified MOKE hysteresis traces and diffraction-based structural descriptors. No fixed process temperatures, minimum meaningful effect, sample size, device tolerances or cost values are supplied. FeCo studies report dependencies on thickness, processing and film structure; those observations motivate careful controls, not a verified BHS mechanism (DOI 10.1088/0022-3727/33/12/304; DOI 10.3390/ma15207191).

## Unit-of-analysis declaration

The *planned specimen/coupon* is one row of the candidate design matrix. Multiple intended MOKE traces per coupon constitute repeated technical measurements and **do not increase** the number of independent specimens. A shared deposition/synthesis batch can induce within-batch dependence; the synthetic plan must label it explicitly. A real laboratory must determine whether processing can actually be assigned independently to coupons within each batch. If not, the treatment unit must be redefined and the plan reviewed again.

The attached example at `research/BHS_V128_MANUFACTURED_DESIGN_FIXTURE.json` uses four artificial deposition batches, each with one reference and one modified coupon. It is a **software fixture**, not a recommended study size or an approved set of laboratory actions.

## Predeclared linear estimability diagnostic

For the candidate *mean processing contrast*, form an integer-coded nuisance design matrix with intercept, synthesis-batch fixed-effect indicators, MOKE measurement-session fixed-effect indicators, and independent within-session linear position trends. Add one binary indicator for the proposed processing arm. Compute exact rational row rank before/after adding the arm:

[
\operatorname{estimable} = \bigl[\operatorname{rank}([X_{nuisance}\mid t]) > \operatorname{rank}(X_{nuisance})\bigr].
]

A nonzero rank increment means only that the processing column is linearly distinguishable from **these declared nuisance columns**. It does not demonstrate causality, physical exchangeability, sufficient power, robust noise estimates, texture mechanisms or laboratory feasibility. Include the number of coupon rows, unique synthesis batches, measurement sessions, intended technical traces, nuisance rank, complete-model rank and residual degrees of freedom.

The program must **explicitly flag** (rather than silently overlook) missing within-batch reference/modified pairing, absent treatment arms in a measurement session, reuse of a session position, missing planned XRD or raw MOKE trace retention, systematic treatment/measurement-session confounding, and a fully saturated design with no residual degrees of freedom. Such failures keep the pilot on hold even if some other algebraic contrast is estimable.

The synthetic fixture is constructed so the processing contrast is distinguishable from batch and session effects, but the initial small example is near-saturated, emphasizing that identifiability alone cannot justify uncertainty intervals or a physical conclusion.

## Strict data and safety boundary

- Plan-only input: unique coupon ID, synthesis batch ID, processing arm, MOKE session ID and planned session position, positive intended technical-trace count, structural readout flag. **No measured coercivity, diffraction intensities, posterior labels or private source outcomes** are accepted in the plan.
- Permitted arm labels: `reference` and `modified`. They stand for two hypothetical contrasts, **not** safe operating recipes.
- The manuscript's physical acceptance conditions remain unresolved: independent partner and permissions, actual instrument calibration records, scientifically permitted processing and controls, composition/thickness confirmation, a meaningful coercive-field difference and measurement precision in A/m, independent synthesis batches, randomized assignment, cost and abstention valuations, uncertainty and power analysis.
- The checker may return `linear_contrast_estimable=true` for a manufactured fixture, but **always** returns `physical_recommendation_allowed=false`, `independent_physical_validation_established=false` and `laboratory_action_allowed=false`.
- A well-formed file or a high matrix rank cannot prove randomization, correct causal adjustment, model calibration or authentic laboratory approval.

## Frozen failure tests

1. All reference coupons in one batch and all modified coupons in another: no valid matched synthesis-batch contrast.
2. The two processing arms in disjoint instrument sessions: session confounding, despite nominal within-synthesis-batch pairing.
3. Processing perfectly aligned with intended early/late measurement position: trend confounding or schedule warning.
4. Repeated measurements from the same specimen falsely represented as new independent coupons: duplicate or invalid provenance rejection.
5. Missing structural scans, missing raw-trace retention, nonpositive trace counts, duplicate session slots, nonfinite or unapproved outcome fields.
6. A numerically full-rank but saturated design is flagged as having zero residual degrees of freedom.
7. Claim/approval flags set to success are rejected or kept in permanent no-go state.
8. No input datasets or calibration/evaluation results from older BHS V11–V12.7 studies are retrieved, and protected seed range `10000..10099` is untouched.

## Next external decision

Seek a collaborator qualified in thin-film synthesis and calibrated magnetic/structural measurements. Ask whether genuinely paired within-deposition batches are feasible, whether specimen assignment can be randomized, and what operational sources of batch and time drift exist. The laboratory must propose and approve an actual sampling design and independent error/precision analysis **before observations**. Any eventual BHS decision policy must compete with a fixed design and appropriate GP/expert references at matched real cost, not against one selected synthetic example.

**Hard gates:** `development_only=true`; `scored_validation_allowed=false`; `independent_holdout_used=false`; `physical_validation_by_bhs=false`; `claim_of_superiority=false`; `causal_identification=false`; `statistical_risk_guarantee_supported=false`; `real_savings_measured=false`.

