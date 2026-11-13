# BHS V12.16 — Preregistered one-input structural provenance experiment and fair-comparison stop rule

**Frozen 13 November 2026 before opening or parsing numerical positions from original `structure_unrel` records.** This protocol extends the outcome-free V12.13–V12.15 source audits. Past failed intakes, original V12.14 element-cardinality rejection, V11 negative real-data result, old draft PRs, default branch and all release tags remain immutable.

## Research question

Can a single archived *original calculation input* be matched to the supposedly initial structure of its specific published source row, without using any segregation energy, relaxed geometry, model score or later measurement? A geometric match is necessary but **not sufficient** to establish chronological availability, global dataset provenance or utility.

Three separate evidence statements MUST remain separate for each proposed predictor:

1. **Origin:** exact source field or independently pinned input file, authorship/source DOI and raw content hashes, candidate `(GB, element, site)` mapping; field existence is not enough.
2. **Pre-computation availability:** evidence that the exact input feature can be obtained before paying for the specific targeted DFT calculation, without consuming forbidden previously hidden results. An initial-coordinate archive proves what was stored, **not** the timing and price of generating that initial structure or selecting candidates.
3. **Policy-time accessibility:** independent chronological trace, dataset split, initial-state generator and decision chronology proving what the BHS/GP/RF selection algorithms can actually see at the instant each action is chosen. Retrospective row presence is **not** such a trace.

No feature is approved for predictive scoring unless all three evidence statements have been separately justified. The available source contains no authenticated global step-by-step decision trace; hence **no new performance experiment** is authorized by this stage regardless of one-sample geometry comparison.

## Fixed source and author example

Article: H. L. Mai and collaborators, *Acta Materialia* **297** (2025) 121288, DOI `10.1016/j.actamat.2025.121288`. Author GitHub repository numeric ID `789358474`; immutable commit `c079fcd00cf1e085fe917d460dbc36a064155296`. Main original `2025_03_02_ptable_Fe_GB_df.csv.gz` Git blob `fcd4e2ef24da093438030e3095469a679ed54d04`, compressed SHA256 `825f0b7c783c51213adb47bd1366023f0861e8a21b904113d9d3871c3daa0fc2`.

Single archived example only:

- Exact original input `Data/S11-RA110-S3-32-He-19/POSCAR.orig`, expected Git blob `c1b92f972db85ebbce5bf9cc8e58a4d356ee27be`.
- Calculation parameters `Data/S11-RA110-S3-32-He-19/INCAR.orig`, expected Git blob `d0a1a818098b901317b1803eb20a4c1db95f54fd`.
- Expected corresponding original CSV key `(S11_RA110_S3_32, He, 19)` from file path; this is a **hypothesis to test**, not an assumed confirmed match. Reject absent, duplicated, or inconsistent identity. Read only that row's `structure_unrel` and selection identifiers; do not parse `E_seg`, `E_seg_unrel`, `structure`, `magmoms` or any computational output. Do not print or commit raw coordinates, full source rows or source data.

## Exact comparison recipe, fixed in advance

1. Fetch and verify upstream identity by numeric GitHub repository ID, exact pinned commit, original compressed CSV source Git blob+SHA256, and sample `POSCAR.orig` + `INCAR.orig` SHA1 Git blobs. Reject byte, size or source mismatches before reading structures.
2. Parse `POSCAR.orig` lattice, species counts and **initial fractional site coordinates**. Refuse unrecognized format, nonfinite values, mixed/partial occupancy, missing species identity, malformed lattice or ambiguous coordinate modes.
3. Parse the matched original CSV `structure_unrel` as a **data-only** pymatgen-style JSON dictionary or a safely literal-evaluated dictionary; do not execute arbitrary serialized content or unpickle anything. Require an explicit `lattice.matrix`, full `sites` list with sole occupied element and `abc` fractional coordinates. No calculated energy/post-run fields may be accessed.
4. Check exact atom number/species multisets, lattice elementwise maximum absolute difference (angstrom), and minimum-image species-stratified site matching using deterministic linear-sum assignment; report only aggregate maximum and mean distances (angstrom). Threshold for an explicitly labeled strict geometric match: **maximum lattice difference <= 0.001 angstrom AND maximum matched site displacement <= 0.001 angstrom**. Record signed test failures as stop conditions; do not relax threshold because results look unfavorable.
5. Synthetic adversarial tests must detect wrong element, site count, lattice, site permutation, fractional cell wrap, coordinate changes and malformed data, plus enforce nonaccess to energy labels.
6. The report must distinguish **author-archived input present**, **sample geometry match**, **global 4,289-row original-input lineage**, **pre-expensive-compute evidence**, and **decision-time policy access** as separate booleans. Even if sample match succeeds, set last three to `false` unless separately authenticated evidence becomes available in a new preregistered study.

## Reference honesty: what is already known about BHS performance

The **existing** V11 retrospective real physical replicate benchmark, frozen before seeing its selection outcomes, compared an inherited BHS v5 kernel-portfolio EI *component*, not the full hypothesis-centric BHS system. Same fixed budget, five DEVELOPMENT seeds: GP–ARD EI mean final regret **7.363 J**, RF–UCB **8.983 J**, BHS v5 **9.368 J**, random **15.951 J**; lower is better. BHS portfolio lost to strong GP/RF and did not establish any independent advantage. No new policy may be called the complete BHS system merely because its source file uses BHS nomenclature. This stage must retain this negative evidence and must not rescore historical V11 development seeds as an independent benchmark. Any future complete BHS vs GP/RF/rule-based comparison requires proof of actual hypothesis representation, updates and acquisition logic, feature chronology parity, equal exact labels and compute budgets, distinct development/held-out groups, and prespecified negative-result criteria.

**Release decision remains `NO_GO_FOR_FAIR_SCORED_COMPARISON`** even on sample geometry success. No real DFT costs, independent future holdout, physical validation, BHS superiority or calibrated guarantees. Protected NIST seeds `10000..10099` remain unused. Public BHS origin/authoring privacy restrictions apply.
