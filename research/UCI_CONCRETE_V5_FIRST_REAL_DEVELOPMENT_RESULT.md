# BHS — First external real-data development result (v5)

**Date:** 6 November 2026  
**Evidence level:** REAL published measurements used in a **retrospective exploratory development** study; no independent held-out validation, no physical mechanism discrimination, no new laboratory measurements.

## Data and source integrity

- Official source: **I-Cheng Yeh**, *Concrete Compressive Strength*, [UCI data set 165](https://archive.ics.uci.edu/dataset/165/concrete-compressive-strength), DOI [10.24432/C5PK67](https://doi.org/10.24432/C5PK67), **CC BY 4.0**.
- UCI source accession: **1,030** rows, **8** features, continuous target in **MPa**.
- Rows at **28 days**: **425**; after eliminating **9** identical-input duplicate rows without viewing labels to decide which to retain: **416** unique candidate profiles.
- Fingerprint of **parsed numeric UCI data**: `98958f558e46763cf6d5403de8784af39ebe906c4604447c188889c3e346cd87`. **Not** a checksum of the original `.xls` file. No source rows redistributed.

## Protocol implemented before the run

Compared random selection, a fixed Matérn-5/2 GP–EI reference, and a likelihood-weighted Matérn-3/2/RBF expected-improvement portfolio. Model families are **statistical approximations, not hypotheses about real chemical mechanisms**. Each method receives the same **6** random initial candidates per seed and makes **10** further selections; development seeds **7, 13, 23**. Only acquired measurements become visible to acquisition policies. The retrospective evaluator computes regret using the full response pool only after decisions.

No observed monetary/energy/time cost model, proper independent held-out set, physically calibrated uncertainties or actual experiments are available. There is **no tuning performed after this run** in the reported result.

## Results

Lower normalized final simple regret is better. Each average includes **three** development campaigns, not repeated measurements of physical generalization.

| Method | Mean normalized final regret | Mean final regret (MPa) |
| --- | ---: | ---: |
| Random | 0.242408 | 17.7467 |
| Fixed GP–EI | **0.095889** | **7.0200** |
| Kernel portfolio EI | 0.097209 | 7.1167 |

By development seed (final regret in MPa):

| Seed | Random | GP–EI | Portfolio |
| --- | ---: | ---: | ---: |
| 7 | 24.53 | 7.25 | 7.25 |
| 13 | 7.25 | 7.05 | 7.05 |
| 23 | 21.46 | 6.76 | 7.05 |

**Primary conclusion:** The statistical kernel portfolio **did not beat** the fixed GP–EI benchmark in this development setting. It tied in two seeds and was worse in one. Both model-guided methods showed lower development regret than random selection on average. This does not establish statistical significance, method superiority, calibrated probability, or a new materials discovery.

## Verification

- [Actual source-code commit and development workflow](https://github.com/busrakisik/inverse-materials-design/actions/runs/42214172524), run `42214172524`: **success**.
- Synthetic/contract tests `tests/test_uci_concrete_v5.py`: **5/5 successful**.
- Exactly **9** matched-budget developmental campaigns; verified exploratory gating fields.
- GitHub Actions aggregate artifact `13500686767`; original JSON SHA-256 `03a3bdb537d43703d1ee618be90a5ccd7493638bb40beaece77714e0d68dfa4e`.
- [Reviewed aggregate-only result file](uci_concrete_development_v5.json). The original artifact is still available through the workflow while retention permits. The reviewed file is a transcription of the verified values, **not byte-identical** to the workflow's complete original JSON.

## Limitations and next falsifiable work

The age-restricted source may include unrecognized repeat mixtures, batch confounding, and measurement variability; input-only duplicate elimination does not make independent observations. The reported optimization is a retrospective **property-search task**, not a falsifiable model of physical mechanisms or a realistic prospective lab. Comparing a small fixed portfolio with one fixed GP is not an exhaustive strong-baseline contest. Three development seeds are insufficient for confidence statements. No experiment cost information is verified.

For further progress, establish a domain-reviewed falsifiable physical question or acquire a distinct, permission-cleared domain and freeze robust baselines, budget, missingness, uncertainty and leakage rules before any independent trial. Any future adjustment informed by these results remains **development**.

**Hard gates:** `scored_validation_allowed=false`, `independent_holdout_used=false`, `physical_validation=false`; independent seed IDs `10000..10099` remain untouched.
