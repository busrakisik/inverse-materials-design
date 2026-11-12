# BHS V12.13 — External ferritic-iron grain-boundary source intake

**Frozen 12 November 2026 before source-row inspection and outcome evaluation.**

## Decision and external provenance

Use genuine external density-functional-theory segregation calculations to examine source integrity, group dependence and feature availability before developing a decision selector. This study is **source-only**, with no performance scores, no original physical measurements and no claims of cost savings or superiority.

Research: H. L. Mai, X.-Y. Cui, T. Hickel, J. Neugebauer and S. Ringer, *A high-throughput ab initio study of elemental segregation and cohesion at ferritic-iron grain boundaries*, Acta Materialia 297 (2025), 121288. DOI: https://doi.org/10.1016/j.actamat.2025.121288 .

Author-supplied public GitHub repository **numeric ID 789358474** (resolve the name through GitHub's repository-ID endpoint, without depending on a mutable branch). Immutable upstream commit: `c079fcd00cf1e085fe917d460dbc36a064155296`. Path: `2025_03_02_ptable_Fe_GB_df.csv.gz`. Expected compressed size: `31745622` bytes; Git blob: `fcd4e2ef24da093438030e3095469a679ed54d04`. README Git blob: `34afd33f1d17bfbe89486a61f123b73324962233`; MIT license Git blob: `b03323b18141efb9cf18c35ac0c4951760dfeda9`. README declares 4,289 rows, 90 columns, six modeled Fe grain boundaries. Compressed SHA-256 is **unknown until actual download**.

The published source license does not independently certify all third-party rights. Retain originator attribution. Do not copy raw upstream data into the BHS public repository.

## Scientific boundaries

Target `E_seg` is relaxed DFT segregation energy in eV, **not an independently measured physical result**. Intake can parse identifiers `GB`, `element`, `Z`, `site`, `GB_site`, `GB_element_site`, `job_name` and outcome *blankness* only. Do not parse target magnitudes to numeric values or calculate prediction errors, regret or proposed measurement savings. Preserve mismatched sources, duplicate IDs, inconsistent element numbers, malformed rows and blank identifiers as **failures**, not silently cleaned success.

No prediction feature is certified as available at decision time. Relaxed structures, energy-derived values, work of separation, DDEC6, magnetic moments, relaxed Voronoi descriptors and other post-calculation attributes are **ineligible**. Even unrelaxed-energy `E_seg_unrel` has no verified chronology or unit cost and must not be treated as an affordable second fidelity.

The same underlying boundary and site may recur across different solutes: rows cannot be independent draws. Consider later family-disjoint GB, element-disjoint and crossed GB-by-element holdouts. A random-row evaluation or row-iid interval is prohibited. With six GB families, no strong population risk guarantee follows. Do not select future holdouts using outcomes. Inspect grouping and missingness metadata, then separately freeze candidate features, complete split IDs, a prospective evaluation plan and equal-information matched GP/ensemble and simple references **before evaluating any outcome**. Actual computation times and costs remain unverified.

## Stop / no-go

A source blob or data-row mismatch must stop further evaluation. This is not a laboratory collaboration or an independent physical validation. Preserve all historical negative results, failed first V12 RF replay, V12.5 calibration failure transfer, draft PRs and released tags. NIST seeds `10000..10099` remain unused.

Gates: `development_only=true`, `scored_validation_allowed=false`, `independent_holdout_used=false`, `physical_validation_by_bhs=false`, `claim_of_superiority=false`, `statistical_guarantee_supported=false`, `real_savings_measured=false`, `physical_recommendation_allowed=false`, `laboratory_action_allowed=false`.
