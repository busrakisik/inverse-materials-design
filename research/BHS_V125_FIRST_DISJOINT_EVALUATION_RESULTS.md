# BHS v12.5 — First disjoint manufactured calibration and evaluation results

**7 November 2026. Development only; not physical evidence or independent generalization.**

## Provenance and frozen design

- Pre-scored protocol: `research/BHS_V125_DISJOINT_CALIBRATION_PROTOCOL.md`, blob `719431338ee9cd0b3ecc50d197b946aeb79c4701`.
- Frozen selector/evaluator source: `scripts/bhs_v125_disjoint_calibration.py`, blob `fa5419b0a65b7b83fafe214d2c18b9df4f0e04e7`.
- Software checks: **88/88 passed**, https://github.com/busrakisik/inverse-materials-design/actions/runs/42381960004.
- Calibration-only run: https://github.com/busrakisik/inverse-materials-design/actions/runs/42382124635, **48 cases**, four groups (101, 103, 107, 109).
- Frozen calibration handoff recorded **before evaluation** in `research/BHS_V125_FROZEN_CALIBRATION_HANDOFF.md` (blob `e39d2dad46ad57fa3c434049a3aaed42a0bfd6ff`).
- Calibration JSON SHA-256: `fe47b0f79d04ff45df39498559d59dbfc941796c2d195dec4b1cfa4e406cfd48`, 39,393 bytes.
- Disjoint evaluation: https://github.com/busrakisik/inverse-materials-design/actions/runs/42382439887, **48 cases**, four unseen-in-calibration groups (211, 223, 227, 229). The run downloaded and verified the exact frozen calibration file before constructing evaluation groups.
- Evaluation JSON SHA-256: `654def586730c51793cf4040752770349a25dbcd4c808da86469a5f649e7b831`, 63,890 bytes. Both original JSON files are in the immutable Actions artifact `13578575387` and separately archived as lossless compressed files in this branch.
- Fixed libraries in CI: Python 3.11, NumPy 1.26.4, SciPy 1.13.1, scikit-learn 1.5.2, pandas 2.2.3.
- Analysis independently rechecked the 48 evaluation rows, the 6-by-3 coverage grid, the accepted error counts and all reported policy losses from the exact JSON, without adjusting any thresholds.

## Primary frozen cap and outcomes

The calibration target is **maximum 0.50 calibration coverage**, not guaranteed coverage on new data. A calibration acceptance must have empirical high-regret frequency no greater than 0.25 among the eight calibration records per policy. `z` thresholds and costs were fixed before evaluation; high regret means evaluator-only latent regret greater than **0.35**. Abstention costs **0.50** latent units. Lower loss is better.

| Policy | Calibration accepted | Evaluation accepted | High-regret / accepted | Mean abstention-adjusted loss | Mean incomplete designs |
|---|---:|---:|---:|---:|---:|
| `evidence_gate_completion` | 3/8 | 4/8 | 0/4 | 0.326967 | 0.00 |
| `evidence_gate_native` | 3/8 | 4/8 | 0/4 | 0.326967 | 2.62 |
| `gp_pooled_noise_ivr` | 4/8 | 5/8 | **2/5** | 0.418752 | 0.00 |
| `gp_ard_bundled` | 0/8 | 0/8 | not estimable | 0.500000 | 0.00 |
| `gp_pooled_noise_ei` | 0/8 | 0/8 | not estimable | 0.500000 | 0.00 |
| `random_bundled` | 0/8 | 0/8 | not estimable | 0.500000 | 0.00 |

The evaluation accepted high-regret fraction for the pooled-noise IVR method is **0.40 (2/5)**, greater than the predeclared empirical calibration cap 0.25. Both high-regret records are two order variants of the **same** evaluation group 227, which uses manufactured between-batch offsets; they are dependent sensitivity variants and cannot be counted as independent physical failures. This result nonetheless falsifies the claim that the empirical calibration cap automatically transfers to every new synthetic group.

The evidence gate methods accepted four evaluation decisions without an observed high-regret event, but only across eight related campaigns. They shared the same recommendation quality under the primary rule; completion protection removed incomplete designs without reducing the observed primary loss. **No calibrated error guarantee or general superiority is established.**

The three always-abstaining methods should not be described as intrinsically poor design optimizers. Their frozen calibration thresholds admitted zero cases, so their observed loss 0.50 reflects the predeclared abstention penalty, not a direct comparison of raw acquisition regret. An evaluation case might exceed a zero-acceptance calibration sentinel; this occurred in none of these eight cases.

The `shifted` landscape occurred only in group 229, and its two response orders are correlated. Success or failure on this one manufactured shifted group provides no external distribution-shift guarantee.

## Scientific interpretation and next acceptance gates

1. A fixed empirical rule on eight correlated calibration cases does **not** prove probability calibration, conditional error control or safe laboratory use. The observed mismatch for IVR is a negative, preserved result.
2. The source-disjointness and one-use oracle ledger prevent direct outcome reuse. This is a software design feature, not proof of real-world generalization.
3. Repeat-order sensitivity, pooled-noise misspecification and the unmatched native-gate completion rule remain limitations. The code explicitly preserves these asymmetries.
4. A future study must specify physically plausible observation chronology, batch and instrument provenance, safety restrictions and actual decision costs; obtain independent investigator oversight and new prospective measurements.
5. Before choosing new coverage rules, analyze the limitations of empirical threshold selection versus finite-sample selective-risk bounds at the *group* level. Any later threshold changes require an openly named new development study, not a rewritten V12.5 result.
6. Original V11 negative data, the non-passing V12 historical replay and V12.3–V12.4 mixed results must remain accessible. No release tag or history was rewritten.

## Evidence restrictions

`development_only=true`; `scored_validation_allowed=false`; `independent_holdout_used=false`; `physical_validation_by_bhs=false`; `causal_identification=false`; `calibrated_uncertainty_proven=false`; `claim_of_superiority=false`; `real_savings_measured=false`; `reserved_nist_seeds_used=false`.
