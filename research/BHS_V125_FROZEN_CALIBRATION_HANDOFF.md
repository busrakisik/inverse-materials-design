# BHS v12.5 — Immutable calibration handoff

**7 November 2026; calibration stage complete; evaluation not executed at the time of this record.**

The original, source-independent calibration was generated on a dedicated branch and CI run. This handoff fixes the exact calibration file that may be used by the subsequent evaluation. The 48 campaigns below are synthetic calibration cases and are not independent physical measurements.

- Original GitHub Actions run: https://github.com/busrakisik/inverse-materials-design/actions/runs/42382124635
- Workflow artifact ID: `13577764466`
- Artifact name: `bhs-v125-calibration-frozen-development`
- Expected JSON archive member: `bhs_v125_calibration.json`
- Exact calibration JSON SHA-256: `fe47b0f79d04ff45df39498559d59dbfc941796c2d195dec4b1cfa4e406cfd48`
- Original JSON Git blob SHA-1: `8c1b3d4fc4d053553efac5d5063091556895120a`
- Exact JSON size: 39,393 bytes; stage `calibration`; 48 rows.
- Frozen protocol blob: `719431338ee9cd0b3ecc50d197b946aeb79c4701`
- Frozen selector and staged evaluation source: `fa5419b0a65b7b83fafe214d2c18b9df4f0e04e7`
- Frozen V12.4 method source: `c7f04720e7a804c3f1e87a43cb34fb0c5834319f`
- Calibration source groups: 101, 103, 107, 109. Evaluation-only source groups: 211, 223, 227, 229.
- Two response orders per group and six policies: 48 calibration cases total.
- Predeclared primary coverage cap `0.50`, empirical calibration error cap `0.25`, latent-regret tolerance `0.35`, abstention cost `0.50`.

## Frozen primary thresholds

| Policy | Threshold (strict score greater than) | Accepted calibration cases |
|---|---:|---:|
| `evidence_gate_completion` | 0.8477701167480189 | 3/8 |
| `evidence_gate_native` | 0.8044692931327522 | 3/8 |
| `gp_ard_bundled` | 3.269441267205532 | 0/8 |
| `gp_pooled_noise_ei` | 3.442949279526623 | 0/8 |
| `gp_pooled_noise_ivr` | 1.5152156768025924 | 4/8 |
| `random_bundled` | 5.029465312231371 | 0/8 |

The evaluation must download the archived calibration file by **fixed run ID and artifact name**, require an exact bytewise SHA-256 match, re-evaluate its content integrity and recompute all thresholds before constructing any evaluation group. No threshold may be changed after evaluation results are observed. If the archive expires or the digest mismatches, evaluation must **fail closed**; do not regenerate calibration and pretend the same source was used.

**Interpretation:** Eight correlated calibration cases per policy cannot establish a reliable true error bound. A 0/8 acceptance result is legitimate and must not be converted into a success claim. No prospective source, externally calibrated uncertainty, real resource savings or superiority claim is supported.

The original V11 negative findings, V12 parity failure and V12.3–V12.4 mixed results are preserved separately. Protected seed range 10000..10099 remains unused.
