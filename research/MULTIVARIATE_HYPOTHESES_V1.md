# BHS — Multivariate Composition Hypotheses v1

**Status: synthetic mathematical prototype, NOT NIST-fitted and NOT independently validated.**

## Why this exists

NIST's pinned Fe–Co–Ni MAT dataset was read by CI (921 inferred sample records) but its element-column order, composition scale, per-sample uncertainty, experimental costs and reuse constraints have not all been verified. This module intentionally does **not** load or fit NIST data. It provides a mathematically testable candidate for three-component composition representation, only after external physical review and source-specific metadata mapping.

## Model

The ordered input `c=(c_Fe,c_Co,c_Ni)` is a **caller-declared assumption**, not inferred NIST metadata. Require finite nonnegative fractions summing to 1. On the composition simplex, three unconstrained linear terms plus an intercept would be collinear; therefore the baseline features use `[1,c_Fe,c_Co]`, treating Ni as the implicit remainder.

The three **phenomenological shape hypotheses**, NOT certified competing physical mechanisms, are:

- **Linear:** `[1,Fe,Co]`.
- **Fe–Co interaction:** `[1,Fe,Co,Fe*Co]`.
- **Localized response:** `[1,Fe,Co,exp(-||c-(1/3,1/3,1/3)||²/(2*0.18²))]`.

The latter two extend the baseline with different fixed nonlinear bases and are nested extensions; Occam factors and prior scales affect model probabilities. Their scientific validity, expressiveness and novelty remain unproven. Location and width of the localized shape are developer choices, not data-inferred or optimized. Units of synthetic response are arbitrary; do not equate them with measured coercivity or Kerr rotation.

For each model `m`: `beta_m ~ N(0, 0.5 I)` and `y | beta_m, c ~ N(phi_m(c)^T beta_m, sigma²)`. Known observation `sigma` is an assumption. Model prior is uniform. Exact Gaussian linear conditional updates yield posterior means and covariance, with marginal predictive evidence used to update model probabilities. Invert precision matrices independently in `batch_reference` to check posterior arithmetic without reusing sequential updates.

## Synthetic contract

- Six deterministic generated observations across a ternary-composition simplex; no real labels, no BHS independent holdout seeds or scoring.
- Strict fail-closed composition, sigma and numeric checks.
- Report posterior family probabilities and max-absolute differences between sequential and independent batch parameter posterior, without making model-success claims.
- CI requires **20 tests** and produces a report with SHA-256; no raw NIST or other external data is downloaded.

## Known limitations and research directions

1. Neither linear/additive, Fe–Co interaction nor localized response has yet been endorsed by a materials expert as a defensible Fe–Co–Ni physics mechanism. These are surrogate hypothesis families.
2. No independent measurement error calibration, handling of repeated measurements, correlation, synthesis failure, outliers or instrument drift.
3. Family comparison is conditional on chosen bases, prior scales, nominal noise and finite candidate set. Nested families may show strong posterior preference even when all are incorrect.
4. This module has **no EIG, cost model, decision policy, active learning benchmark or physical validation**. Never interpret its posterior as a measured materials prediction.
5. Need to verify Fe/Co/Ni column semantics, target alignment, data quality and legal reuse conditions before adapting real source. Current NIST dataset inspection reports only aggregates.
6. Future pilot must freeze a domain-reasoned hypothesis specification and credible strong baselines before independent evaluation; do not access independent BHS holdout seeds 10000..10099.

## Commands

```bash
python -m pip install numpy==1.26.4
python -m unittest discover -s tests -p 'test_multivariate_hypotheses_v1.py' -v
python -m scripts.multivariate_hypotheses_v1
```

All results must state `scored_validation_allowed=false`, `independent_holdout_used=false`, `nist_data_used=false`, and `physical_validation=false`.
