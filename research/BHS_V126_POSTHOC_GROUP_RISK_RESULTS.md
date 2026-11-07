# BHS v12.6 — Read-only group dependence report

**7 November 2026. Methodological post-result audit only, not a new evaluation, prospective validation or independent physical study.**

## Original sources and integrity

This report groups the **already-known V12.5 evaluation decisions** by their original source group. It does not change any acquisition decisions or frozen calibration thresholds.

- Original calibration JSON SHA-256: `fe47b0f79d04ff45df39498559d59dbfc941796c2d195dec4b1cfa4e406cfd48`.
- Original evaluation JSON SHA-256: `654def586730c51793cf4040752770349a25dbcd4c808da86469a5f649e7b831`.
- Both compressed source archives on `bhs-v125-evidence-archive` were decompressed and verified byte-for-byte in the v12.6 GitHub Actions run.
- Frozen method implementation: `scripts/bhs_v126_group_risk_intake_contracts.py`, Git blob `19b2aa364a4677a20f20e69d30666ff0bf9a29f6`.
- Frozen original methods and v12.6 protocol were separately checked by Git blob identity.
- Complete 104 software tests passed; successful audit and one-use archive checks: https://github.com/busrakisik/inverse-materials-design/actions/runs/42384207824.
- Original post hoc audit JSON SHA-256 `fa302c04e21385c3df3c48f69b01ed97dab0a770aecfeff954a9bc576254b6a1` (8,218 bytes); lossless XZ SHA-256 `a326dd927921a0b957992dda24a49701c1c8128f194489fc4fe0d9f13a783e04` (908 bytes). Original workflow artifact ID `13578218396`.
- This branch stores an exact lossless copy: `research/bhs_v126_group_risk_audit.json.xz`.

## Group-aware interpretation at the frozen 0.50 calibration-coverage setting

The two measurement-order variants in the same source share the same latent landscape, underlying measurements and batch structure. They **cannot** be treated as independent experimental source groups.

| Frozen method | Accepted decisions / 8 | Covered source groups / 4 | Failed covered groups | Hypothetical iid 95% group-error upper |
|---|---:|---:|---:|---:|
| Evidence gate, completion constrained | 4 | 2 | 0/2 | 0.7764 |
| Evidence gate, native | 4 | 2 | 0/2 | 0.7764 |
| GP pooled-noise IVR | 5 | 3 | **1/3** | 0.8646 |
| GP–ARD bundled | 0 | 0 | undefined | not estimable |
| GP pooled-noise EI | 0 | 0 | undefined | not estimable |
| Random bundled | 0 | 0 | undefined | not estimable |

The two GP–IVR high-regret decisions (2/5 accepted individual decisions in the prior V12.5 record) arise from **one** of the three covered source groups. Defining a group failure as *any accepted decision in that group* with regret above 0.35 produces **1/3 failed covered groups**, not 2/5 independent group failures.

The group upper limits here are intentionally labeled **hypothetical**. They would require independent, identically distributed source groups and appropriate fixed/independent selection conditions. Actual evaluation groups share manufactured generation structure and have no independently established physical sampling distribution. The numeric intervals therefore **cannot be used as generalization bounds, safety guarantees or validated calibration**.

Even under the hypothetical iid assumptions, zero failures over four independent groups would imply one-sided 95% upper 0.5271; reducing that upper bound to at most 0.25 with zero failures requires **at least 11 independent groups**. The current archive has only four groups, and for some methods only two covered groups. Eleven groups is an illustration of statistical sample size, not a sufficient prospective physical protocol.

All automated recommendation gates remain closed: `physical_recommendation_allowed=false`, `independent_validation_established=false`, `statistical_guarantee_supported=false`.

## Prospective structural source contract

The new source-independent validator refuses data with missing/duplicate replicate identifiers, absent explicit time zones, out-of-order timestamps, negative or invalid uncertainty/cost/duration, inconsistent units, or overlapping sample designs and synthesis/measurement batches across calibration and evaluation.

Passing these *syntactic and internal consistency* checks does not authenticate data owners, validate apparatus calibration, certify scientific noise assumptions, prove investigator approval or substitute for laboratory safety assessment. Human investigators must inspect original instrument logs, authentic approvals, source rights and domain-specific constraints. No real physical data were imported in this audit.

## Preserved negative evidence and next decision

- Original V11 inferior comparator results remain unchanged.
- Original V12 failed historical RF parity replay remains marked nonpassing.
- V12.3 and V12.4 mixed/null improvements remain unchanged.
- V12.5's calibration-transfer gap for GP–IVR remains negative evidence; no threshold was retuned.
- The original Git branches, release tags, historical citations and protected seeds remain untouched.

**Next defensible step:** identify investigator-supervised prospective experimental collaborators and precommit a domain-specific, physically interpretable loss function, actual measurement budgets, independent batch/group splits, timestamped replicate acquisition and safety approval. No external physical performance claim is authorized from these synthetic records.

Mathematical reference: Clopper and Pearson, *Biometrika* 26, 404–413 (1934), DOI 10.1093/biomet/26.4.404; this method alone does not address selected conditional risk or dependence.

## Evidence gate

`development_only=true`; `scored_validation_allowed=false`; `independent_holdout_used=false`; `physical_validation_by_bhs=false`; `causal_identification=false`; `calibrated_uncertainty_proven=false`; `claim_of_superiority=false`; `real_savings_measured=false`; `reserved_nist_seeds_used=false`.
