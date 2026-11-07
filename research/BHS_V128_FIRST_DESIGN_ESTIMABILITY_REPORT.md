# BHS v12.8 — First design estimability diagnostic (no physical outcomes)

**7 November 2026. Development-only, source-independent, manufactured design fixture.**

## Exact record and test result

- Branch: `bhs-v128-design-estimability-contracts`, implementation commit `a69729c8130f1dfb15890da6c06a2defc4675187`.
- Protocol prepared before any outcomes: `research/BHS_V128_DESIGN_ESTIMABILITY_PROTOCOL.md` (no results, physical measurements or laboratory authorization).
- Frozen illustrative plan: `research/BHS_V128_MANUFACTURED_DESIGN_FIXTURE.json`, original SHA-256 `ad54b0d2f9a19685ee749b171b58cd045c5c08c061a527c56c91968c9704195b`, Git blob `3cde6a6ad809effdf21fcdd50ab737c8cfaf07e8`.
- Code: `scripts/bhs_v128_design_estimability.py` Git blob `de89ac8d63485afd59b0076c4ea075a12475f089`.
- Adversarial tests: `tests/test_bhs_v128_design_estimability.py` Git blob `144a287e4117394aa7c3733c40fc63e409439cb2`.
- CI run: https://github.com/busrakisik/inverse-materials-design/actions/runs/42393803510, **SUCCESS, 140/140 tests** (122 inherited, 18 new). The original Actions artifact has ID `13581958783`.
- Exact first output JSON SHA-256 `700668f2a14f3146d00d5309caff6c6887b0c4d86dfc618b81990d21278602c2`, 1,028 bytes, Git blob `8a3d9a4b1f6779fe627d09524f6e0edb82485205`. An identical copy is stored as `research/BHS_V128_FIRST_DESIGN_ESTIMABILITY.json`.

## First result

| Diagnostic | Result |
|---|---:|
| Fabricated coupon rows | 8 |
| Independent **named** synthesis batches | 4 |
| MOKE measurement sessions | 2 |
| Intended technical MOKE traces | 24 |
| Rank of nuisance matrix | 7 |
| Rank including the processing indicator | 8 |
| Residual degrees of freedom | **0** |
| Processing contrast estimable under declared additive nuisance columns | **Yes, algebraically only** |
| A usable physical uncertainty estimate | **Not established** |
| Genuine physical measurements | **None** |
| Approved laboratory procedure or new physical evidence | **None** |
| Software release decision | **NO_GO_PHYSICAL_DESIGN_NOT_EXTERNALLY_VALIDATED** |

All eight specimens are purely manufactured identifiers. The rank increment 7-to-8 proves only column distinguishability in the *declared linear matrix*. Because the model is saturated, residual variance cannot be estimated in this toy plan; no confidence interval, effect precision, predictive calibration or sample-size justification follows. Three repeat traces per coupon are **not** three independent deposited coupons. Four named deposition batches do not demonstrate real between-batch independence without external provenance.

## Tested negative cases

- Treatment assigned by separate synthesis batches: batch/processing confounding detected.
- Treatment assigned by separate MOKE sessions: session/processing confounding detected.
- Treatment systematically scheduled earlier/later: session-position imbalance flagged.
- Duplicate coupon or session position, missing raw MOKE or XRD plan, wrong units, malformed/nonfinite effect, fabricated outcome fields or claimed laboratory approval: rejected.
- Increasing technical trace counts does not increase coupon or independent batch counts.
- All outcome and external approval flags remain false, even where the algebraic contrast is estimable.

## Next external steps

An equipped researcher must first determine whether matched reference/modified coupons **can actually be produced within independently replicated deposition batches** and whether assignment/randomization is physically feasible. The lab must verify sample composition, thickness, substrate, processing constraints, authentic MOKE/XRD instrumentation, sweep geometry, uncertainty, measurement time and order, real costs, safe practice, source rights and meaningful effect in A/m. A proper sample-size/precision analysis and independently defined calibration/evaluation partitions are prerequisites to any prospective measurement study.

This is a **first design failure/limitation report**, not a newly verified magnetic mechanism or physical discovery. Original V11 negative findings, the nonpassing first V12 historical parity replay and V12.3–V12.7 mixed/no-go findings remain unchanged. No historical release tags, source datasets, protected seeds or public default branch were altered.

**Hard gates:** `independent_physical_validation_established=false`; `physical_recommendation_allowed=false`; `laboratory_action_allowed=false`; `statistical_risk_guarantee_supported=false`; `real_savings_measured=false`.
