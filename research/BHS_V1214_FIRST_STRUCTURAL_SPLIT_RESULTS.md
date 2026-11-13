# BHS V12.14 — First full outcome-free group-disjoint split readiness report

**13 November 2026. No numerical segregation-energy values read, no model fitted, no experimental intervention, no empirical cost or risk guarantee.**

## Traceable source, chronological failure, and independent correction

Input: Mai et al., *Acta Materialia* 297 (2025), 121288, DOI `10.1016/j.actamat.2025.121288`. External author-published DFT source from GitHub repository numeric ID `789358474`, commit `c079fcd00cf1e085fe917d460dbc36a064155296`, original compressed file Git blob `fcd4e2ef24da093438030e3095469a679ed54d04`, SHA-256 `825f0b7c783c51213adb47bd1366023f0861e8a21b904113d9d3871c3daa0fc2`. No upstream rows or source numerical outcomes have been redistributed in BHS.

1. Original precommitted V12.14 split code, commit `2c54ba6d91dc9e331a15bf7b185d69f032112c4c`, source-only CI [43381953005](https://github.com/busrakisik/inverse-materials-design/actions/runs/43381953005): **FAILED** because it required exactly 90 source element labels. Its adversarial and inherited software tests passed; failed source assumption stays public and unmodified.
2. Independent frozen discrepancy protocol, CI [43382312875](https://github.com/busrakisik/inverse-materials-design/actions/runs/43382312875): **SUCCESS**, found 91 distinct original element labels. Earlier 90 applied only to records with an original nonmissing combined identifier; one source row belongs to element `Yb`, omitted from that prior subset.
3. Separately frozen corrected observed-cell protocol, CI [43382787966](https://github.com/busrakisik/inverse-materials-design/actions/runs/43382787966), head `7a0141716b0453e6353b1aa5dfa1d4e310e5bfe8`: **SUCCESS 259/259 software tests** including 20 new split tests and inherited contracts. This is a *passing metadata-structure audit*, not a scientific predictive result.

## First corrected outcome-free manifest

- GitHub original artifact ID **`14016589159`**, run `43382787966`. Manifest file `bhs_v1214_first_observed_cell_manifest.json`, **775,333 bytes**, SHA-256 **`f0524c1e328cbd01af4f6a428229cead1e3b780c80d5cd9567c65aac3e4e675f`**. The exact manifest is retained as GitHub Actions run evidence, and is deterministically regenerated from immutable source bytes and source code; do not reinterpret a later run as its first-run original.
- Full source: **4,289** distinct primitive `(GB, element, site)` tuples, six GB labels, **91** source element labels, **54** distinct `GB_site` identifiers. All 54 structural site identifiers recur across source rows; that does **not** make them 54 independently sampled physical experiments.
- **30** missing relaxed segregation-energy strings, source outcomes not inspected numerically. Exactly **110** original missing combined identity fields remain missing; their primitive tuples are unique.
- Frozen fold counts: **6** leave-one-GB-out (LOBO), **91** leave-one-element-out (LOEO), **541** observed GB–element crossed folds. Five possible GB–element combinations are **absent from the source**: the five GBs other than `S5_RA001_S310` with `Yb`. No zero-row crossed test fold was fabricated.
- Crossed held-out test rows: **minimum 1, maximum 14**. Crossed target-nonblank rows: **minimum 0, maximum 14**. Exactly **one** crossed fold has no nonblank target strings: `S5_RA001_S310` × `Yb`. This cell is `NOT_SCOREABLE_TARGETS_ABSENT`, not a scientific failure or a zero-energy observation.
- For every crossed fold, all rows sharing its GB or its element but not both are embargoed; all train rows have neither group. The source-only CI checked 4,289 rows partitioned exhaustively into disjoint train/test/embargo keys in all 541 crossed folds.
- LOBO may reuse element labels across train/test; LOEO may reuse the same GB and `GB_site` identifiers across train/test. The manifest explicitly reports these overlaps rather than treating the folds as independent physical validation.

## Scientific boundary and next action

This verifies that retrospective *split manifests* can be constructed without touching numerical outcomes. It **does not** prove a usable physical hypothesis, accurate model, sufficient independent holdout, compute-cost advantage, calibrated selective risk, or a meaningful acquisition policy.

The first actionable scientific barrier is not another validation wrapper: **certify descriptors actually available before running each expensive DFT calculation**. Solute atomic number and selected GB are known inputs; raw site indices do not constitute transferable physical geometry. Relaxed coordinates, calculated energies, magnetic moments, DDEC6 and DFT-based unrelaxed energetics must not be treated as free information. Establish original pre-calculation structure provenance, candidate-only geometric descriptors, actual DFT run chronology/cost, nonrandom missingness, reference GP/RF and decision objective *before* any scored run. If this cannot be certified, keep a no-go decision and seek a better source or an independent scientific partner.

Hard gates: `development_only=true`, `scored_validation_allowed=false`, `independent_holdout_used=false`, `physical_validation_by_bhs=false`, `claim_of_superiority=false`, `real_savings_measured=false`, `statistical_guarantee_supported=false`, `laboratory_action_allowed=false`.

Original negative results V1–V12.12, original V12.13 failed intake, source artifacts, public default branch and release tags, earlier draft PRs, and protected NIST seeds `10000..10099` remain untouched.
