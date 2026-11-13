# BHS V12.14 — Source element-cardinality discrepancy, diagnostic protocol

**Frozen after the original failed split-readiness run, before examining its missing element identities.**

The original preregistered `bhs-v1214-group-split-readiness` code at commit `2c54ba6d91dc9e331a15bf7b185d69f032112c4c` must remain unchanged. GitHub Actions `43381953005` failed when `EXPECTED_ELEMENTS=90` was checked against all original rows. All 16 newly introduced split tests and the inherited scientific contract tests had passed before the source-only stop. V12.13's earlier 90-element count was drawn from the 4,179 rows with a nonempty originally supplied combined identifier; it may not represent all 4,289 original rows. Preserve both facts rather than retroactively certifying the first run.

Use the exact same original immutable 31,745,622-byte compressed DFT file, Git blob `fcd4e2ef24da093438030e3095469a679ed54d04`, SHA-256 `825f0b7c783c51213adb47bd1366023f0861e8a21b904113d9d3871c3daa0fc2`, upstream commit `c079fcd00cf1e085fe917d460dbc36a064155296`, public GitHub repository numeric ID `789358474`.

Read **only** source `GB`, `element`, `Z`, `site`, `GB_element_site` and blankness (not magnitude) of `E_seg`. Compare element sets in records with vs without combined IDs; count source rows for any elements absent from the complete-ID subset. Report full element symbol set, complete-ID subset, incomplete-ID subset, set differences, six-GB coverage for each, and counts by missingness. Avoid material energy values, candidate performance, source modification or winner selection. Do not force an expected number of elements before observing this metadata. Preserve any novel composition, spurious string or missing source fields as documentary evidence requiring qualified interpretation.

The next split protocol may update the prespecified 90-element assumption *only after this diagnostic report is preserved*. This is an eligibility correction, not a revised successful first V12.14 run. No scored validation, out-of-source holdout, acquisition, physical measurements, cost claims, model superiority or statistical risk guarantees.
