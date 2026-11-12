# BHS V12.13 — First external DFT source intake, rejection, and primitive-key audit

**Date: 12 November 2026. Source metadata only. No model, posterior, physical experiment, scientific superiority or verified computation cost.**

## Why this milestone matters

The project moved from manufactured schedules to independently authored published computational materials data, without presuming that a density-functional calculation equals measured physical truth. Data are from Mai and collaborators, *Acta Materialia* 297 (2025), 121288, https://doi.org/10.1016/j.actamat.2025.121288 . External public source repository numeric ID `789358474` at immutable commit `c079fcd00cf1e085fe917d460dbc36a064155296`; MIT license is stated in the author's repository.

The compressed upstream file `2025_03_02_ptable_Fe_GB_df.csv.gz` is `31,745,622` bytes. Independently verified Git blob `fcd4e2ef24da093438030e3095469a679ed54d04`; compressed SHA-256 `825f0b7c783c51213adb47bd1366023f0861e8a21b904113d9d3871c3daa0fc2`. Source contains 90 columns and six modeled Fe grain boundaries. No raw dataset has been duplicated into the BHS public repository.

## Chronological original outcomes — do not overwrite

1. **First preregistered strict intake failed**, GitHub Actions run [43254272297](https://github.com/busrakisik/inverse-materials-design/actions/runs/43254272297). All 223 inherited and new unit tests passed, but the independent source-only check refused the raw data. It counted 4,179 rows passing every identity field and flagged `MISSING_REQUIRED_IDENTITY` plus an apparent `ROW_COUNT_MISMATCH`. This mismatch was caused by the validator counting only fully identified records rather than all source records. First raw report SHA-256 `45d4b114e26247aba16cdf5fcbd04cd5c64e4eecffceb0e701ce72f0c768d520`, GitHub Actions artifact ID `13960312377`. The *failure remains a failure*; it is not relabeled as passing.
2. **Frozen outcome-free diagnostic passed**, run [43255084351](https://github.com/busrakisik/inverse-materials-design/actions/runs/43255084351), with 14 inherited source tests and 5 additional diagnostic tests. All **4,289 physical record rows** were counted; **110 were missing exactly one combined identifier**, `GB_element_site`, with no other mandatory identifier blanks. Thirty rows had blank target strings. Original report SHA-256 `cb546b036849110c7b155f190149eac59285721b8aaf437e101145300d1e5a05`; artifact `13959748536`.
3. **Prerecorded primitive-key recoverability test passed**, run [43255890692](https://github.com/busrakisik/inverse-materials-design/actions/runs/43255890692): 4,289 nonblank **unique tuples** `(GB, element, site)`; zero duplicate primitive tuple keys, zero duplicate job names, zero inconsistent tuples mapping to multiple published combined names. The 110 original missing combined IDs **remain missing in the raw source**. Among 30 records with blank target strings, 20 also lack a combined ID. Original metadata report SHA-256 `fc32ac91d4aea1c1f332cab2380a27b1c144f0e73502c010ad62e1597989e6be`; artifact `13960194540`.
4. Intermediate diagnostic test failures [43255729299](https://github.com/busrakisik/inverse-materials-design/actions/runs/43255729299) and [43255865890](https://github.com/busrakisik/inverse-materials-design/actions/runs/43255865890) were implementation/test-name corrections, **not successful science**. Corrected CI retained the original protocol and source. Both failed jobs are part of the traceable software record.

## Accepted scientific conclusions

- Exact upstream bytes and origin are pinned and verified. All 4,289 records are distinguishable by a **separate derived tuple**; the raw combined identifier has 110 missing values. This supports a *potential metadata-level recovery*, not an unauthorized modification of original values.
- Thirty source target strings are blank. Do not impute, silently drop or infer missing-at-random. Explicit missingness policy is needed before any scored study.
- There are six grain-boundary geometries and 90 elements; 540 grouped boundary-element combinations in the stricter intake. These are dependent calculations from one source, not independent labs, new physical measurements or an untouched physical holdout.
- Outputs `E_seg` are computed relaxed DFT segregation energies (eV). No computation durations, financial costs, separately authenticated fidelity levels or action timing have been verified.
- Pre-run scientific descriptors have **not** been certified. Do not use relaxed structure, DDEC6, magnetic moment or energy-derived fields to predict the same calculation; an unrelaxed DFT value must not be treated as free or cheaper without real acquisition-cost evidence.

## Next decision gate

A separate, preregistered benchmark design is required: admissible *pre-calculation* features, signed scientific meaning, disjoint GB/site/element grouping strategy, real versus count-only budget, source-missingness policy, strong matched GP/ensemble/reference comparators, locked model/hyperparameter selection, evaluation isolation and publication claims.

**Do not proceed to outcome scoring until this gate is established.** The first source-only rejection and later diagnostics are valuable because they expose assumptions that a naive random-row materials benchmark would miss.

Gates: `development_only=true`, `scored_validation_allowed=false`, `independent_holdout_used=false`, `physical_validation_by_bhs=false`, `claim_of_superiority=false`, `statistical_guarantee_supported=false`, `real_savings_measured=false`, `physical_recommendation_allowed=false`, `laboratory_action_allowed=false`. Protected NIST seeds `10000..10099` unused. Public default branch, old releases and historical V1–V12.12 negative findings remain unchanged.
