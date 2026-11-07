# BHS v10 — Real-materials replicate dependence and validation leakage

**7 November 2026 — completed, source-locked, retrospective DEVELOPMENT-ONLY experiment.**

## Executive scientific finding

The dataset contains **1,800 physically measured mechanical responses** but only **600 unique 3D-printed designs**, each tested three times. A random measurement-row split placed **92.4% of test measurements at exact geometries already observed in the model's training set**, whereas a geometry-grouped split had **0% such overlap**.

With the **same prespecified Random Forest reference** in five development splits, mean test MAE was **3.8129 J** for random-row splitting versus **4.7920 J** for strictly grouped splitting, a difference of **0.9790 J** (~25.7% relative to the row-split MAE). The two splits target **different generalization questions**, so this discrepancy must not be attributed entirely to feature leakage or treated as a causal effect. This is direct evidence that a measurement-level train/test report is **not a valid stand-in** for unseen-geometry performance when repeated geometries overlap.

This outcome is **not** proof that a BHS acquisition method beats a baseline, that its uncertainties are calibrated, or that a physical laboratory decision is safer.

## Original authentic experiment and provenance

- Liang, Q., Gongora, A. E., Ren, Z., et al. (2021), *Benchmarking the performance of Bayesian optimization across multiple experimental materials science domains*, npj Computational Materials **7**, 188, DOI [10.1038/s41524-021-00656-9](https://doi.org/10.1038/s41524-021-00656-9).
- Original crossed-barrel experiments: Gongora, A. E., Xu, B., Perry, W. et al. (2020), *A Bayesian experimental autonomous researcher for mechanical design*, Science Advances **6**, eaaz1708, DOI [10.1126/sciadv.aaz1708](https://doi.org/10.1126/sciadv.aaz1708).
- Source repository `PV-Lab/Benchmarking` (MIT license), immutable commit `7585c517ad88e676c42c6bf24a8ad278e01ddb21`, `datasets/Crossed barrel_dataset.csv`.
- Exact Git blob SHA-1: `b007fe5d8762233bbd23c8cf83858b169f05492a`.
- Original CSV raw-byte SHA-256: `2c01f875f3c210e986ca6142bf20f417884c2ad7d6f008c2fc574b44a3d5f606`.
- Four geometry inputs `n`, `theta`, `r`, `t`: number of columns, twist angle, outer radius and wall thickness. Original experimental outcome is toughness (J), the area under an actual force–displacement curve. The **original groups**, not BHS, performed physical printing and mechanical testing.

## Predeclared design and test unit

The study protocol [was committed before reading aggregate response results](BHS_REPLICATE_LEAKAGE_AUDIT_V10_PROTOCOL.md). The source was fetched only after its immutable Git hash matched. Every geometry must have **exactly three** measurement rows; missing, nonfinite, geometrically invalid or unrecognized measurements cause a hard failure.

For each development seed `7, 13, 23, 31, 43`, 25% of measurement rows are selected for a row-level test. Independently, a **GroupShuffleSplit** selects 25% of distinct geometry groups for a geometry-level test (150 designs, all 450 corresponding measurements). The predictor is fixed at 120 trees, minimum leaf size 2 and seed-specific deterministic setup. Model fitting never receives test outcomes.

A row-level split answers performance on another measurement when the model may already have observations from the same design. A group-level split answers performance on **unseen combinations of geometric inputs within the sampled experimental grid**. They are not equivalent scientific claims.

## Actual measured repeatability

| Statistic across 600 exact geometry groups | Value |
| --- | ---: |
| Triplicate groups with nonidentical toughness | 600 / 600 |
| Median sample SD within a geometry | **1.6605 J** |
| 90th-percentile within-geometry sample SD | **8.7906 J** |
| Median within-geometry measurement range | **3.0401 J** |
| 90th-percentile within-geometry range | **16.1940 J** |
| Largest within-geometry range | **37.2980 J** |
| RMS deviation about each observed geometry mean | **4.3296 J** |

These variations may reflect printing, testing, environmental, batch or material effects; the downloaded five-column dataset does **not** identify their causes or independent instrumentation noise. The observed triplicate sample standard deviations should **not** be presented as calibrated model uncertainty.

## Predictor comparison — fixed reference only

| Development seed | Random-row MAE (J) | Strictly grouped MAE (J) | Row-test share with geometry already in training |
| --- | ---: | ---: | ---: |
| 7 | 3.9331 | 4.2903 | 94.67% |
| 13 | 3.8608 | 4.6238 | 91.33% |
| 23 | 3.8159 | 5.0574 | 93.33% |
| 31 | 3.7267 | 5.1582 | 90.00% |
| 43 | 3.7281 | 4.8302 | 92.67% |
| **Arithmetic mean** | **3.8129** | **4.7920** | **92.40%** |

The strictly grouped evaluation includes 450 measurement outcomes from **150 completely unseen geometries** per seed. The random-row evaluation includes 450 measurements but extensively revisits geometries present in training. Same measurement count does **not** mean matched geometry coverage, and five overlapping development splits do not give independent statistical confidence or evidence of real-world deployment utility.

A simple exact-geometry sample-mean lookup has **zero coverage** in grouped holdout by construction and can only be evaluated on previously seen row-test geometries. It is not a prospective physical optimization baseline.

## BHS decision and necessary next evidence

**`REQUIRE_GEOMETRY_GROUPED_EVALUATION_FOR_NEW_GEOMETRY_CLAIMS`**

Reason codes: repeated measurements are not distinct geometries; row-split geometry overlap; unknown independence of printer/batch/process; no untouched prospective evaluation. This decision prevents a real measured dataset from being used to justify an **unmeasured type of generalization**.

Next, within **development only**, implement group-level, label-isolated pool-based selection with matched experimental-measurement budgets. Compare domain-appropriate strong GP-ARD and RF methods against any proposed BHS policy, measure observed replicate variability and report all negative outcomes. A genuinely independent prospective laboratory study must collect new outcomes with controlled batch/instrument provenance and prespecified selective-risk/coverage and physical cost criteria.

## Verification and restrictions

- [Research implementation](../scripts/bhs_replicate_leakage_v10.py) · [13 synthetic source/integrity tests](../tests/test_bhs_replicate_leakage_v10.py) · [original protocol](BHS_REPLICATE_LEAKAGE_AUDIT_V10_PROTOCOL.md)
- [Authentic aggregate-only experimental audit](bhs_replicate_leakage_v10.json), saved from a successful source-locked workflow.
- [Full successful GitHub Actions run](https://github.com/busrakisik/inverse-materials-design/actions/runs/42345271849). The same verification reran the 13 contract tests, fetched the immutable source, checked geometry-group separation, and archived the result.
- Raw original measurements are **not copied into this repository**; study output reports aggregated metrics and source checksums.
- `development_only=true`; `scored_validation_allowed=false`; `independent_holdout_used=false`; `physical_validation_by_bhs=false`; `calibrated_uncertainty_proven=false`; `causal_identification=false`; `method_superiority_claimed=false`; `measured_cost_savings=false`. Independent NIST seed range `10000..10099` remains untouched.

**Scientific conclusion:** The most consequential v10 result is an *evaluation-design correction*, not a claimed algorithmic advance. The next independent lab collaboration must treat **physical measurement replicates, novel design support and experiment provenance** as first-class constraints.
