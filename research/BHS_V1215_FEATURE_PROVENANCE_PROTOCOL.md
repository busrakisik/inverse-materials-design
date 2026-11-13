# BHS V12.15 — Preregistered source feature-availability and computation chronology audit

**Frozen 13 November 2026, before auditing availability of candidate fields across the immutable original 4,289-row external CSV.**

## Scientific question and exclusion

Are *potentially pre-relaxation* material/geometry fields actually present in the public source, and does any evidence establish that they were available **before** the expensive DFT decision being proposed? Availability alone is not chronological provenance. This audit shall only examine **column names, missing-string indicators, and primitive group identities**. Never read, convert, aggregate or print scientific numerical values of energies, structural coordinates, Voronoi measurements or convergence. The only `E_seg` operation is blankness detection. No learning, physics outcomes, model selection, posterior inference, or acquisition policies are authorized.

Source: H. L. Mai et al., *Acta Materialia* 297 (2025), 121288, DOI `10.1016/j.actamat.2025.121288`. External GitHub repository numeric ID `789358474`, immutable commit `c079fcd00cf1e085fe917d460dbc36a064155296`; original CSV compressed SHA-256 `825f0b7c783c51213adb47bd1366023f0861e8a21b904113d9d3871c3daa0fc2`, Git blob `fcd4e2ef24da093438030e3095469a679ed54d04`.

The peer-reviewed article's Data Availability section claims initial and final structures in its tabulated pickle, whereas the CSV may omit structures. The authors' README lists `structure_unrel`, `site_z_unrel`, `dist_GB_unrel`, and 16 `VorNN_*_unrel` descriptors in its overall dataset column documentation. **Do not resolve this documented packaging discrepancy by assumption**; record actual CSV header presence/absence and blankness separately from what the pickle allegedly supplies.

The author's pinned external repository also has an example original starting-configuration `Data/S11-RA110-S3-32-He-19/POSCAR.orig`, Git blob `c1b92f972db85ebbce5bf9cc8e58a4d356ee27be`, and `INCAR.orig`, blob `d0a1a818098b901317b1803eb20a4c1db95f54fd`. These show source-provided **sample** input artifacts, not a per-row lineage chain, a verified wall-time, or evidence that a full input file was independently available at each adaptive decision.

## Prespecified groups and treatment

1. **Selection-time known inputs:** `element`, `Z`, and `GB` (what calculation is proposed). `site`, `GB_site`, `GB_element_site`, `job_name` remain row/group identifiers, *not* transferable continuous predictors. Element and GB identity cannot prove generalized physical features on their own.
2. **Conditional starting-geometry candidates:** exact field `structure_unrel`, `dist_GB_unrel`, `site_z_unrel` and names beginning `VorNN_` and ending `_unrel`. Their existence and completeness are checked without inspecting values. The suffix `_unrel` **does not certify** that the field was generated prior to any DFT run, was selected without outcome feedback, or was available without costly preprocessing. **No automatic whitelist promotion.**
3. **Reference-state or chronology-sensitive unknowns:** pure-GB energies, moments, cleavages, convergence, site multiplicities, equivalent-site indices and any other column whose original generation timeline is not documented remain unapproved.
4. **Forbidden free predecision measurements:** `E_seg`, `E_seg_unrel`, all Wsep, DDEC6, relaxed `structure`, `site_z`, `dist_GB`, `magmoms`, `magmom_solute`, all explicitly computed outputs and potentially expensive surrogate labels. An `unrel` *energy* is not free static input; it also comes from a quantum calculation. General default-deny applies to all unreviewed fields.

## Source-only audit and reproducibility commitments

Read all 4,289 rows from exact immutable CSV; require six GB groups, 91 element labels, 110 originally missing combined IDs and 30 empty target strings exactly as V12.14 first manifest. Require a unique `(GB, element, site)` key and consistent `Z` per element (using V12.14 source-only metadata contract). Record sorted entire 90-column CSV header set and header digest. Report each candidate field's header presence, populated/blank row counts, and per-GB populated counts, plus conditional candidate availability for rows with vs without target strings (target missingness only). Do not record raw row identifiers, individual values, structures or scientific outcomes in the exported report. Unknown columns must be explicitly counted and marked unapproved, not silently treated as features. All results deterministic and invariant to row order, label-magnitude changes, and hypothetical string feature values that preserve blankness.

**Stop criteria:** any changed source checksum, primitive identity/missingness mismatch, header change, malformed source record, unintentionally inspected numerical target, unpinned source artifact, or attempt to promote an available field to an approved predictor without independent chronology evidence. The first run's failures remain failures. We must **not** train on candidate inputs or report predictive performance during this audit.

## What could establish future admissibility

An audited starting `POSCAR`/pymatgen structure must map to each candidate's exact `(GB, element, site)`, be demonstrably generated before relaxation/energy feedback, and support stable input-only local geometry descriptors with signed units/conventions and no post hoc site selection. When only a retrospectively published starting structure exists, permit a later analysis as **retrospective**, not as experimentally held-out or guaranteed truly prospective. Compute time or financial cost must come from genuine logs or remain count-only. Provide scientific rationale for physically independent split families and convergence/missingness.

**V12.15 remains NO-GO by default** even when coverage is 100%. Flags: `development_only=true`; `scored_validation_allowed=false`; `precalculation_geometry_certified=false`; `real_cost_verified=false`; `independent_holdout_used=false`; `physical_validation_by_bhs=false`; `claim_of_superiority=false`; `statistical_guarantee_supported=false`; `real_savings_measured=false`; `laboratory_action_allowed=false`. Preserve the original failed V12.14 run and subsequent diagnosis/reproduction; no changes to public default branch, draft PRs, past negative evidence, release tags or protected NIST seeds `10000..10099`.
