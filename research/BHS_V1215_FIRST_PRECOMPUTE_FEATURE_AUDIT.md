# BHS V12.15 — First source feature-availability audit; chronology NOT certified

**13 November 2026. Preregistered outcome-free analysis of original third-party DFT source. No numerical structure, energy, cost or model result inspected.**

## Identity and original first run

- Scientific source: Mai et al., *Acta Materialia* **297** (2025) 121288, DOI `10.1016/j.actamat.2025.121288`. External GitHub repository numeric ID `789358474`; immutable upstream source commit `c079fcd00cf1e085fe917d460dbc36a064155296`; original `2025_03_02_ptable_Fe_GB_df.csv.gz` compressed Git blob `fcd4e2ef24da093438030e3095469a679ed54d04`, SHA-256 `825f0b7c783c51213adb47bd1366023f0861e8a21b904113d9d3871c3daa0fc2`.
- First protocol and source code preregistered independently of the actual candidate-column coverage: `research/BHS_V1215_FEATURE_PROVENANCE_PROTOCOL.md` Git blob `dee8a1cc15f273ab3163cb3a4f489ebc538ed0c2`; `scripts/bhs_v1215_precompute_feature_provenance.py` `e0d4076612b5bdd42fca9f39256d131be1e2a98b`; 14 new adversarial tests `de1c4c8eba6f7656f4de024be922377851be4e30`.
- GitHub Actions first run [43401314429](https://github.com/busrakisik/inverse-materials-design/actions/runs/43401314429) **SUCCESS, 273/273 software tests** (inherited 259 and 14 new). Original first JSON evidence artifact ID **`14024579181`**, original file `bhs_v1215_first_source_feature_coverage.json`, **31,827 bytes**, SHA-256 **`e6316cf9fedde1abbc630a369f923b49a4f75458f4041422dab4cfc4c4f5cc5f`**. The independent reproduction pipeline must match the original bytes and digest, not simply rerun a materially modified protocol.
- Preserved source contract: 4,289 unique primitive `(GB,element,site)` tuples, **six** GB groups and **91** element labels; **30** empty target strings; **110** empty originally published combined identifiers; no numerical outcome inspected. Source primitive key digest `b119d939bbe0dd00367b5029437be9ae0e363bb7d1ff5e1c0d8fcf3679fb7601`.

## Actual 90-column source findings, not paper assumptions

The original CSV indeed has these three columns: `structure_unrel`, `site_z_unrel`, `dist_GB_unrel`. It also contains **19** `VorNN_*_unrel` fields: coordination count, total volume, total area, and the 16 face-statistic descriptors. **Total candidate unrelaxed geometry fields: 22**, without approving any as predecision predictors. Note that the article's Data Availability text says its CSV is *without structures* while the actual immutable CSV contains `structure_unrel`: the actual checked artifact and source claim are recorded separately rather than merging inconsistent statements.

All **22** candidate columns had the same availability counts: **4,285 nonblank string records, four blank records**. All four candidate blanks were in the single boundary label `S9_RA110_S2_21`. For each field, the **30 rows with missing target-energy strings had a nonblank candidate field**; the four blank candidate fields occur in rows whose target-energy strings are nonblank. Thus missing candidate coverage and missing label strings are not the same phenomenon. We have **not** inspected whether the four missing-field rows coincide *across* candidate columns individually; equal group/total counts do not mathematically prove row-identity overlap.

All 90 column names are represented in the original JSON, with a SHA-256 digest of the deterministic sorted header set `8ffd3f3678ab96963413b3a7f3ef8040d8f62e25bd8733c28ee0506ab1ad21c2`. Column provenance category counts:
- `SELECTION_KNOWN_IDENTITY`: **3** (`GB`, `element`, `Z`);
- `IDENTIFIER_ONLY_NO_PREDICTION`: **4**;
- `CANDIDATE_UNREL_GEOMETRY_NOT_CERTIFIED`: **22**;
- `COMPUTED_OR_POSTRUN_DENY`: **35**;
- `COMPUTED_OR_UNCERTAIN_DENY`: **19**;
- `UNKNOWN_PROVENANCE_DENY`: **7**, including one **unnamed empty-header column** whose origin is not justified.

The source author's pinned example original calculation input `Data/S11-RA110-S3-32-He-19/POSCAR.orig`, Git blob `c1b92f972db85ebbce5bf9cc8e58a4d356ee27be`, and `INCAR.orig`, Git blob `d0a1a818098b901317b1803eb20a4c1db95f54fd`, show that **one sample input is archived**. It does **not** document the 4,289 candidate input histories nor establish source-feature timing, original data selection or compute cost. Initial `structure_unrel` being present is **not proof** that its descriptors are safe, cheap, stable, complete or free of feedback-derived leakage.

## NO-GO decision and scientifically useful next work

1. **Only schema/coverage is validated**. No geometry predictor has been approved; `E_seg_unrel` and unrelaxed magnetic moments are calculation outputs, not free inputs. All other fields default deny.
2. **Next genuine research question:** Can each published `structure_unrel` be proven to correspond to an original, exactly keyed, pre-run POSCAR or pristine configuration, and can an input-only local descriptor be reproduced without seeing a relaxed structure or energy? A separate prerequisite protocol must freeze structure parsing and input-to-output chronology before reading any numerical coordinate. One matched sample is not general certification.
3. Independently establish true computation budgets/time, convergence and nonrandom missingness, and meaningful scientific choice of candidate before any matched GP/RF/BHS comparison. Source comes from one retrospective computational campaign, not physical out-of-source validation.

**Hard gates remain:** `development_only=true`, `scored_validation_allowed=false`, `precalculation_geometry_certified=false`, `real_cost_verified=false`, `independent_holdout_used=false`, `physical_validation_by_bhs=false`, `claim_of_superiority=false`, `statistical_guarantee_supported=false`, `real_savings_measured=false`, `laboratory_action_allowed=false`.

Prior NIST and source failures, V12.12 conditional studies, V12.13 first failed source intake, V12.14 first failed 90-element gate, old default branch/releases/tags and all unmerged draft PRs are preserved. Protected NIST seeds `10000..10099` not touched.
