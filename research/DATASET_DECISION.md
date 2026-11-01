# BHS Dataset Gate v1 — Research decision record
Date: 2026-11-01
Status: DATASET_CANDIDATE_SELECTED / REAL_DATA_NOT_INGESTED / BENCHMARK_NOT_RUN

## Decision
Use Matbench v0.1 `matbench_expt_gap` (4,604 composition entries; experimental band gap in eV) as the FIRST real-data ingestion and offline selection pipeline validation. Use Matbench Discovery WBM (unique-prototype subset) as a LATER domain-aligned materials discovery evaluation candidate, subject to an explicit leakage assessment and a properly implemented hypothesis-conditioned policy. The two tasks measure different scientific endpoints and must never be conflated.

## Scope of the first real-data stage
- Purpose: verify actual public data ingestion, labels/units, reproducible IDs, non-leaking data access, and baseline selection under matched budgets.
- It is NOT CHGNet validation, crystal stability, a materials discovery benchmark, or evidence of BHS superiority.
- No BHS policy advantage claim until an explicit scientifically meaningful hypothesis representation and calibrated evidence model exist.
- Do not download datasets inside ordinary CI tests; stage data under a controlled dataset acquisition workflow with hashes, source, version, license and citation.

## Preregister before any held-out outcome inspection
1. Record exact download source and published dataset version, raw SHA-256, dataset license/attribution, row count and expected columns (`composition`, `gap expt`).
2. Determine any missing/invalid/duplicate composition handling using only training data; no labels of test candidates for tuning.
3. Freeze family/composition group definitions and train/validation/test manifests before policy tuning. Standard Matbench folds alone do not prove family-disjoint splits.
4. Select one scientific acquisition objective in advance (e.g., band gaps closest to a target *specified before evaluation*), with target rationale; do not maximize gap by default without stating its scientific purpose.
5. Freeze budget K and seeds, and pre-register primary best-so-far acquisition endpoint; report held-out test problem grouping and uncertainty appropriately.
6. Baselines: seeded random without replacement, public-feature ranking learned/tuned on train only, and at least one nontrivial sequential ML selection baseline. BHS is withheld from comparison until a genuine evidence-update policy exists.
7. For each selection step, reveal ONLY the queried label to the policy. Never pass the full ground-truth map to a policy; audit for side channels in feature preprocessing.
8. Separate selection-performance claims from regression-prediction leaderboard scores; these are different tasks.

## Next implementation gate (no data downloaded yet)
Build a fail-closed dataset manifest validator that rejects missing source, licensing, unit, hashing, split definitions, label-visibility guarantees, and unapproved objectives. Test with fake metadata, but never generate synthetic 'real dataset performance'.

## Scale-up scientific target
Matbench Discovery WBM data: DFT-corrected formation energy and energy above hull are distinct target properties. Version and license must be pinned, and evaluate with unique-prototype/non-overlap measures given potential training overlap of existing MLFFs such as CHGNet. A known stable label from DFT is not equivalent to predicted CHGNet potential energy. The full Figshare bundle may be >16 GB; stage only necessary verified components first.

## Sources reviewed
- https://hackingmaterials.lbl.gov/matminer/dataset_summary.html
- https://github.com/materialsproject/matbench/blob/main/matbench/matbench_v0.1_dataset_metadata.json
- https://doi.org/10.6084/m9.figshare.22715158
- https://github.com/janosh/matbench-discovery/blob/main/data/datasets.yml
- https://github.com/janosh/matbench-discovery/blob/main/data/wbm/readme.md
- https://doi.org/10.1038/s42256-025-01055-1
