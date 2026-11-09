# BHS v12.12 — First outcome-free paired-precision sensitivity results

**9 November 2026. Conditional design algebra, not physical measurement or independent validation.**

## Frozen source and test evidence

- Inherited branch: `bhs-v1211-public-lead-evidence-archive`, parent HEAD `2651e9ab2f88bf38b4f2532e5c2ae51997f2414e`.
- Protocol blob `335e7e6b9698c6f9c80ef95954049776bcc28d4f`; implementation blob `2140c109f0540a32a8559808fc79ca1874cb16a6`; tests blob `bc2a93a7bfb97a61a6f130ef0636efdae9ac239a`.
- Historical manufactured fixture SHA-256: V12.9 `e65e85a6c2d1a8fed749fdd3502c9021343ca53bb01fb0ec06306101961abde6`; V12.10 `adc920e2eba62c7e86ad93b227a0327c692952e0bbb2036907c38326974a5a42`. No underlying fixture modification.
- GitHub Actions run `42629101178`, head `bb3079291c11f597df249a05b7dbef4cf928cf51`, **SUCCESS: 209/209 software tests** (196 inherited, 13 new), with original output artifact `13680575661`.
- Deterministic result JSON `runs/bhs_v1212_first_sensitivity.json`, SHA-256 `6dc26a852774b9cf2785971c99203d4b4ad52b4954fb79bad82253a44ed178c4`, produced locally and checksum-verified in GitHub CI.

## Complete-schedule exact coefficients

Conditional model: independent zero-mean run, MOKE-session, coupon, and per-trace effects. The primary linear contrast is the mean of the eight paired within-block differences (modified minus reference). This is not the regression estimator audited in the earlier structural checks. Coefficients multiply *variance* terms; no actual magnitudes are known.

| Historical manufactured layout | Complete pairs | Run | MOKE session | Coupon | Trace average |
|---|---:|---:|---:|---:|---:|
| V12.9 cross-session paired | 8 | 0 | 0 | 1/4 | 1/12 |
| V12.9 within-session paired | 8 | 0 | 0 | 1/4 | 1/12 |
| V12.10 postdeposition coupon scope | 8 | 0 | 0 | 1/4 | 1/12 |
| V12.10 deposition-run scope | 8 | 1/4 | 0 | 1/4 | 1/12 |

These zeros are conditional cancellations within these specific balanced layouts, **not evidence that batch drift, measurement-session effects or physical confounding do not exist**. V12.10 deposition-run scope has sixteen separately named proposed deposition runs vs eight in coupon scope; neither set of runs is independently verified.

## Hypothetical, dimensionless sensitivity illustration

With coupon and trace standard deviations each fixed to one arbitrary common unit, and with either 0, 1 or 2 units of run variability, the model-based standard deviations of the paired mean are:

| Run standard deviation / coupon standard deviation | Postdeposition coupon scope | Deposition-run scope |
|---|---:|---:|
| 0 | 0.5774 | 0.5774 |
| 1 | 0.5774 | 0.7638 |
| 2 | 0.5774 | 1.1547 |

All complete layouts have session coefficient zero because the particular arm allocations balance session offsets. Thus the frozen session ratios 0, 1 and 2 give the same *full-layout* values; this is not a general session-independence guarantee.

## Missing-data counterexample

- Lose one MOKE session from V12.9 cross-session paired layout: **0 surviving complete pairs for both possible session losses**. The paired contrast is not estimable.
- Lose one MOKE session from V12.9 within-session paired layout: **4 complete pairs for each possible loss**. That is structural survival, not a precision or reliability guarantee.
- Lose one matched pair from the cross-session layout: the MOKE-session variance coefficient becomes **2/49** for each of eight deletions; it remains **0** for each one-pair deletion in the within-session layout. With a purely illustrative session SD of 2, and unit coupon/trace SD, the paired-mean SD is **0.7377** vs **0.6172** after one matched pair is removed.
- No adjusted treatment model, missing-not-at-random mechanism or valid cluster-aware confidence interval was evaluated. Fragility under lost pairs must not be recast as a physical discovery.

## Decision and next physical dependency

**Decision:** `NO_GO_PHYSICAL_PRECISION_AND_LAB_FEASIBILITY_UNRESOLVED`.

Without a laboratory investigator's independent verification of the actual intervention, true experimental-unit independence, MOKE calibration, Fe/Co/Ni composition and thickness, paired sample feasibility, realistic variance decomposition and genuine run/session costs, one cannot choose a practical design, compute real power, claim reliability or allocate physical measurements. The next high-value evidence is an approved, prospectively logged and externally reviewable source of actual manufacturing and measurement variation, not further optimization of manufactured layouts.

`development_only=true`; `scored_validation_allowed=false`; `independent_holdout_used=false`; `physical_validation_by_bhs=false`; `formal_power_or_precision_established=false`; `claim_of_superiority=false`; `real_savings_measured=false`; `physical_recommendation_allowed=false`; `laboratory_action_allowed=false`.

All V1–V12.11 negative and mixed findings, release records, old tags, default branch and the protected historical NIST seed range remain unchanged.
