# BHS V12.14 — Corrected observed-cell split design after frozen source-cardinality rejection

**13 November 2026. Prespecified after first V12.14 failure and the separate successful metadata diagnosis, before examining any numerical `E_seg` values.**

## Unaltered first-stage record

- Original V12.14 structural plan and implementation, source branch `bhs-v1214-group-split-readiness` head `2c54ba6d91dc9e331a15bf7b185d69f032112c4c`, produced **FAILED** GitHub Actions run `43381953005`. Tests passed, but its prespecified complete-source element count of 90 was rejected. Keep the failure unchanged.
- Frozen diagnostic branch `bhs-v1214-element-coverage-diagnostic` verified the raw compressed source with GitHub run `43382312875`: full set **91** element labels, complete original-combined-identifier subset **90**, one additional label `Yb` with **one source row**. This matches the upstream source paper's limitation around Yb but does not independently prove the target value or run convergence.
- Never relabel first-run failure, silently delete the Yb row or overwrite missing identifiers. The 110 originally missing `GB_element_site` values and 30 missing target strings remain intact.

## Corrected split universe, fixed before next report

All **4,289 source rows** are identity-eligible under unique `(GB, element, site)` tuples. Require **six** GB identities and **91** element labels. Preserve raw outcome blankness and every excluded/unavailable record.

1. `leave_one_gb_out`: six GB-held-out partitions. Rows sharing a GB belong to one side; elements may overlap and must be reported as such.
2. `leave_one_element_out`: 91 element-held-out partitions including Yb. GB identities and `GB_site` may overlap between training/test, and any all-blank target partition is marked `NOT_SCOREABLE_TARGETS_ABSENT`.
3. `crossed_gb_element`: generate a separate held-out test for each **observed** pair `(GB, element)`. Do not invent test cells for absent pairs; record `6*91 - number_of_observed_cells` separately. Train has neither selected GB nor element, test has both, and the other two quadrants remain embargoed. Never use embargo records for fitting, validation or hyperparameter selection.

Publish for every partition: counts of source rows and target-*nonblank* rows (not outcome values), missingness, common GB/site/element identifiers across train/test, SHA-256 of the sorted primitive keys, the full set of observed and missing `GB x element` cells and structurally empty/all-blank holdout counts. Do not treat target availability as successful convergence. **No numerical target values may be parsed or printed.**

An observation-free metadata audit is *not* a future independent holdout. The combined-source DFT data and fold definitions have already been inspected; any future performance experiment on this source is retrospective. Six GB units and a single published data generation workflow cannot support out-of-lab physical generalization claims.

## Inputs and non-goals

Provisional selection-time identities: element symbol and atomic number `Z`, GB identity; `site` and `GB_site` are grouping information, not transferable physical coordinates. The only candidate numeric descriptor is `Z`; it is insufficient to justify a serious predictive model without certified pre-relaxation geometry. Relaxed geometry, post-run energies, DDEC6, moments and calculated structural data remain prohibited as free pre-run predictors. `E_seg_unrel` is not certified as lower cost. No wall-time, computational budget, customer cost or externally verified source rights beyond the published license have been established.

**Decision gate stays CLOSED after a successful split audit.** Before any scored study, independently pre-register admissible pre-calculation geometry and provenance, missingness, train-only tuning, source-level independence, strong GP/RF/ensemble baselines, decision utility, count-only vs actual cost, and negative-result rules. If none can be certified, stop rather than producing a misleading demonstration.

Source pin: upstream commit `c079fcd00cf1e085fe917d460dbc36a064155296`; compressed SHA-256 `825f0b7c783c51213adb47bd1366023f0861e8a21b904113d9d3871c3daa0fc2`; original Git blob `fcd4e2ef24da093438030e3095469a679ed54d04`; original source is never copied into public BHS.

Hard states: `development_only=true`, `scored_validation_allowed=false`, `independent_holdout_used=false`, `physical_validation_by_bhs=false`, `claim_of_superiority=false`, `statistical_guarantee_supported=false`, `real_savings_measured=false`, `laboratory_action_allowed=false`. Keep old failures, releases, default branch and protected NIST seeds `10000..10099` unchanged.
