# BHS V12.14 — Frozen pre-outcome group-disjoint eligibility audit

**Protocol frozen 13 November 2026, before running this audit or inspecting any numerical segregation-energy outcomes.**

## Scientific decision

The next step after the V12.13 original failed intake and metadata-only recovery is a *split feasibility and information-availability audit*, not a performance benchmark. The immutable external ferritic-iron grain-boundary DFT source remains repository numeric ID `789358474`, upstream commit `c079fcd00cf1e085fe917d460dbc36a064155296`, compressed file `2025_03_02_ptable_Fe_GB_df.csv.gz`, SHA-256 `825f0b7c783c51213adb47bd1366023f0861e8a21b904113d9d3871c3daa0fc2`; Git blob `fcd4e2ef24da093438030e3095469a679ed54d04`.

The source paper is Mai et al., *Acta Materialia* **297** (2025), 121288, DOI `10.1016/j.actamat.2025.121288`. This is one retrospective DFT research collection, not externally prospective physics or an independent laboratory benchmark. It contains 4,289 rows, six source GB labels, 90 element labels and 30 target blanks (first V12.13 audit). The 110 missing original combined IDs remain untouched; primary metadata identity is a separate unique tuple `(GB, element, site)`. Preserve the original failed intake and all first-run hashes.

## Prespecified unit hierarchy

- Row: individual stored calculation-site candidate; not an independent experimental replicate.
- `GB_site`: repeated atomic-site identity across solutes, potentially correlated.
- `(GB, element)`: a group of sites under one boundary and one solute; not a sample of independent labs.
- `GB`: only **six** source boundary geometries; effective out-of-boundary family count is at most six for design.
- `element`: nominal 90 source element identities, repeatedly used across GBs and sites.

All folds are deterministic, based **solely** on primitive identifiers. No random seeds or numerical targets are used.

## Frozen partitions

1. `leave_one_gb_out` (LOBO): six source GB labels, each tested in turn; all rows of a chosen GB are held out from training. Since labels for all six GBs are source-derived, there is no externally untouched future dataset and no reliable population confidence claim from six families.
2. `leave_one_element_out` (LOEO): 90 solute identities, each tested in turn; each element's rows are excluded from training. Site geometries may still be shared, and the method must not claim independent new physical structures.
3. `crossed_gb_element`: 6 × 90 intersections. Test only the selected GB–element cell. Training excludes **every row of both** the selected GB and the selected element; two bridge quadrants are embargoed. No group or element may straddle the train/test split. Tiny cells must be reported as tiny, never called powerful independent tests.

For each family, publish source-only counts, numbers of target-nonblank rows, missing target counts, unique site identifiers, and SHA-256 digests of *sorted* full primitive tuple identities for train/test. Freeze canonical encoding, sorting and assignment rules in tested code. Do not store raw source rows or scientific target magnitudes in BHS.

A nonempty observed `E_seg` string is not evidence that the DFT run converged or is scientifically usable. Missingness may not be at random; no observed targets are imputed. More work is required to audit convergence and source computation inclusion rules **before** scoring.

## Candidate information at action time

- `element`, `Z`, and `GB` are *selection-time identities*: the solute element, its atomic number, and chosen pre-existing GB must be known to define an intended calculation. `Z` is a candidate numeric identity descriptor, not evidence of useful prediction.
- `site`, `GB_site`, `job_name`: identity and grouping only; site numbers are not comparable physical coordinates across GBs. Any geometric site descriptor derived from pristine starting configurations needs an explicit pre-calculation provenance certificate.
- `sigma` and tilt-axis category are published structural metadata for the six boundaries, but not yet locked numerical model inputs; different boundary IDs cannot alone encode an unseen GB.
- `E_seg`, `E_seg_unrel`, `Wsep`, relaxed `structure`, `VorNN`, `DDEC6`, calculated `magmom`, relaxed `dist_GB`, convergence and similar computed properties: **ineligible as freely available pre-evaluation predictors**. In particular, a pre-relaxation DFT energy remains a costly computation and its genuine cost tier is unverified.
- Any other column is *unknown until reviewed*; default deny.

**No scored benchmark, GP comparison, posterior calibration or acquisition optimization is authorized in V12.14.** A later independent protocol must define pre-calculation feature construction and source chronology, realistic costs or clearly labeled count-only evaluation, user decision utility, strong GP/RF/ensemble baselines, train-only tuning, holdout and missingness policies and explicit negative-result stopping criteria. Never use V12.14 folds as a claim of independent validation.

## Fail-closed checks

Require exact source bytes and 4,289 primitive identities, six GB identities, 90 element identities, zero duplicate primitive tuples, 110 absent original combined names and 30 target blanks (only string missingness). Require all partitions disjoint and exhaustive with the embargo groups excluded from training; require stable digests independent of source row order; reject duplicate identities, invalid identifiers, mismatched source. Refuse automatic GO even if all structural checks succeed.

Flags remain `development_only=true`, `scored_validation_allowed=false`, `independent_holdout_used=false`, `physical_validation_by_bhs=false`, `claim_of_superiority=false`, `real_savings_measured=false`, `statistical_guarantee_supported=false`, `laboratory_action_allowed=false`. All old failures, default branch, draft PRs and protected NIST `10000..10099` remain unchanged.
