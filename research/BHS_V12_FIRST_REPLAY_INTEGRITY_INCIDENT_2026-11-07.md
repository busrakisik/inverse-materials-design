# BHS v12 — First historical replay: strict parity failure and source-order diagnostic

**Date:** 7 November 2026. **Status:** INVALID FOR PREDECLARED STRICT V11 PARITY; exploratory development artifact retained, NOT independent or physical validation.

## Exact reproducibility anchors

- Source-pinned replay run: https://github.com/busrakisik/inverse-materials-design/actions/runs/42358170449 (commit `de47ebe8cbbc65636267b5a917019522931848f1`, test steps successful, historical replay executed, strict baseline parity failed).
- Frozen research implementation: `bb366662f18a451595dc6506636d1d984c1fcc01`, source script Git blob `25ad70029af5d3b9f67cff5b00749e7c2e1f2690`.
- Raw public source SHA-256 (verified internally, source data not redistributed): `2c01f875f3c210e986ca6142bf20f417884c2ad7d6f008c2fc574b44a3d5f606`.
- Exact uploaded ZIP SHA-256: `f9e0e52232565861cf0c61b32d1e99a64213f08ba981034720fd3c5e4738b5fb`.
- Unzipped result JSON SHA-256: `09db4b5237f56ff7d8798150a18e9fc5a30ff6e4756c0c0d92faa0ad41e756b0`.
- The original artifact contains only aggregate and seed/policy-level metrics, no original source rows, observed triples or selected design IDs. Its ZIP bytes are archived in this research branch; do not overwrite it with a corrected run.

## Critical finding

The 20 requested campaigns each reached the 48-response budget. The 14 other bundled baseline *regret comparisons* match V11 within the strict tolerance; `seed=43, rf_ucb_bundled` fails: V12 final regret `7.469131473333334 J` versus V11 `11.79736825 J`, a `4.328236776666664 J` discrepancy. Because the workflow explicitly required all 15 baseline-regret comparisons to match, the run is **not a passed V12 scientific result**.

A separately executed, source-locked diagnostic identified the source of divergence: https://github.com/busrakisik/inverse-materials-design/actions/runs/42358546002 . With the original file order, all five V12 RF action sequences reproduce V11 exactly. With the predeclared artificial within-geometry order, seed 31 diverges first at new-design decision 6 (one differing action), and seed 43 diverges at decision 3 (eight differing actions). That is direct evidence of acquisition sensitivity to measurement ordering. The precise floating-point or model implementation mechanism has not yet been isolated; do not attribute it definitively to one source of numerical instability. Crucially, original source order is not established historical measurement chronology.

## Provisional exploratory summary — NOT PASSING STRICT PARITY

| Policy | Mean final completed-design empirical regret (J) | Mean completed geometries | Mean partial geometries |
| --- | ---: | ---: | ---: |
| random_bundled | 15.950972933 | 16.0 | 0.0 |
| gp_ard_bundled | 7.362952481 | 16.0 | 0.0 |
| rf_ucb_bundled | 8.117215571 | 16.0 | 0.0 |
| evidence_gate_development | 7.327793815 | 15.0 | 2.8 |

Evidence gate versus GP–ARD per seed: 7 (11.701 vs 10.243 J, worse); 13 (1.767 vs 8.505 J, better); 23 (7.790 vs 7.790 J, same); 31 (5.138 vs 5.138 J, same); 43 (10.243 vs 5.138 J, worse). The approximately 0.035 J favorable mean is descriptive only: **one win, two ties, two losses**. It is not scientific superiority, statistical significance, stable optimization gain, validated cost savings or a basis for automated laboratory action.

## Decision and next controls

1. Do not change or erase the original frozen protocol, failed run, V11 negative result, source hash, DOI or archived artifact.
2. Study permutation invariance and baseline fragility in a clearly separate development protocol; do not relax the first run's parity gate after seeing the results and call it a pass.
3. If a source-order-invariant implementation is added, label it as a distinct version and freeze its code and criteria before a new development replay. Repeated use of the explored historical archive remains DEVELOPMENT ONLY.
4. Future scientific validation requires independently collected prospective measurements with actual batch/order provenance, a GP adaptive-repeat comparator, fixed risk/coverage/cost definitions, and expert-reviewed physical hypotheses.

`development_only=true`, `scored_validation_allowed=false`, `independent_holdout_used=false`, `physical_validation_by_bhs=false`, `claim_of_superiority=false`, `reserved_nist_seeds_used=false`. Reserved NIST seeds `10000..10099` were not used.
