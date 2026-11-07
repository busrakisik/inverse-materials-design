# BHS v10 — Replicate-aware external materials evaluation audit

**Status at protocol creation (7 November 2026): predeclared exploratory study; no results examined, no independent validation.**

## Source and research rationale

The source is an **authentic high-throughput mechanical experiment dataset**, not a simulation generated for BHS: Q. Liang et al., *Benchmarking the performance of Bayesian optimization across multiple experimental materials science domains*, npj Computational Materials 7, 188 (2021), DOI [10.1038/s41524-021-00656-9](https://doi.org/10.1038/s41524-021-00656-9). Its crossed-barrel mechanical structures originate from Gongora et al., *A Bayesian experimental autonomous researcher for mechanical design*, Science Advances 6, eaaz1708 (2020), DOI [10.1126/sciadv.aaz1708](https://doi.org/10.1126/sciadv.aaz1708).

Source repository: [MIT PVLab benchmarking](https://github.com/PV-Lab/Benchmarking), public MIT software license; original authors must be credited. Immutable source commit `7585c517ad88e676c42c6bf24a8ad278e01ddb21`, exact file `datasets/Crossed barrel_dataset.csv`, Git blob SHA-1 `b007fe5d8762233bbd23c8cf83858b169f05492a`. Programmatically verify the **Git blob checksum**, not merely a URL or the repository's current main branch.

The publication reports **600 distinct geometries each experimentally tested three times**, yielding **1,800 real toughness measurements**. The four design inputs are number of columns `n`, twisting angle `theta`, outer radius `r`, and wall thickness `t`; toughness is computed from a force–displacement experiment (joules). Independent source examination confirms the CSV schema and 600 distinct feature vectors with three reported repetitions; full target statistics have **not** been used to choose this protocol.

## Research hypothesis and falsification

**Question:** Would an apparently normal random row-wise train/test split overstate model generalization to *new physical geometries* because separate repeat measurements of an identical geometry appear in training and test?

Comparison is about **evaluation validity and replicate dependence**, *not* superiority of BHS over an experimental optimizer.

- H0 (practical null): Row-level and geometry-grouped validation of the same frozen reference model have comparable predictive error; neither metric misrepresents generalization to new geometry after accounting for actual train/test support.
- Alternative: Row-level validation is substantially contaminated by previously seen geometry IDs and can report different error than geometry-grouped validation. Do **not** prespecify that the error *must* be lower; the result may be negative, inconclusive, or reverse.
- Generalization target: previously **unseen geometry configurations** within this experimental design grid; not new printer batches, materials, laboratories, future measurements, or real-world safety.

## Frozen experiment design (before fitting to source targets)

1. Download the exact source only with explicit `--execute` in CI; verify blob ID, 1,800 rows and five-column `n,theta,r,t,toughness` schema, finite numeric values and physically plausible geometry bounds. Fail instead of silently replacing missing measurements.
2. Group by the exact four-dimensional geometry vector; demand **600 distinct groups, exactly 3 observations per group**. Never treat those 1,800 observations as 1,800 independent design choices.
3. Audit descriptive repeatability: within-geometry sample standard deviation and range distributions; pooled within-geometry root-mean-square residual around the geometry's observed mean. These are **descriptive** measures, not calibrated observation or instrument uncertainty.
4. Freeze the **same reference predictor** in both evaluation protocols: `RandomForestRegressor(n_estimators=120, min_samples_leaf=2, max_features=1.0, random_state=seed, n_jobs=1)`, scikit-learn `1.5.2`. This is a methodological control, **not** a claim that the predictor is optimal.
5. Use prespecified **development-only seeds `7,13,23,31,43`**, excluding reserved independent-evaluation seeds `10000..10099`. For each seed evaluate a random **25% test-row split**, and separately a **25% test-geometry split** with `GroupShuffleSplit`. Train only on each respective training set; use target values only within the training set while fitting.
6. Report test-set MAE and RMSE in *joules*, number of distinct test geometries, and **fraction of test measurements whose exact geometry already occurs in training**. A simple exact-geometry lookup baseline may report error **only on row-split test geometries observed in training**; its coverage is zero for group-wise held-out geometries.
7. Predefine summaries: per-seed raw counts, mean/median/range across five exploratory seeds, and numerical differences between row and grouped MAE. Do not calculate a p-value, assert independent confidence, or tune a model based on these repeated development partitions.
8. Save source citation, Git blob ID, parsed-table SHA256, aggregate repeat statistics, split support, sample counts, model hyperparameters and diagnostics **only**. Do not commit 1,800 source measurements, per-row outcomes, or source-reactive predictions.

## Necessary scientific limits

- A **group-wise held-out development fold is not an untouched independent validation study**. Source and diagnostic choices have been examined during development; this benchmark cannot be repurposed as a confirmatory external holdout.
- Data originate from a prior **real physical experiment**, but **BHS did not run any experiment**. No claim of new synthesis, materials discovery, increased strength/toughness or measured savings.
- Three repeats may share printer, process, day, material lot or operator context. The accessible CSV has *no documented record per measurement* of these factors; tests cannot certify batch, time or laboratory independence.
- A model's prediction error difference between these two split types may reflect changed test population and support, not solely label leakage or a causal mechanism.
- The comparison is a **measurement and evaluation audit**, not a new Bayesian policy, physical hypothesis test or demonstration of useful laboratory recommendation/abstention decisions.

## Next experimental milestone, conditional on this audit

If the dataset passes integrity checks, define a **separate frozen** replicate-aware pool-based optimization study comparing strong **GP-ARD** and **RF** reference methods, plus an auditable BHS approach. Require group-level label isolation, observed measurement noise, matched *physical measurement counts*, and publish failures. Later obtain independently collected experimental outcomes and domain expert review before any claim about decision safety or commercial utility.

Hard gates: `scored_validation_allowed=false`, `independent_holdout_used=false`, `physical_validation_by_BHS=false`, `method_superiority_claimed=false`. The original paper's experimental status does not authorize new independent-validation claims for BHS.
