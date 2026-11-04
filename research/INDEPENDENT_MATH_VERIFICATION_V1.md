# BHS — Independent Mathematical Verification v1

**Status: development-only numerical/mathematical audit. Not external independent validation, not peer reviewed, and no holdout.**

## Audited assumptions

Current BHS `competing_hypotheses_v2` considers three one-dimensional bases, linear, quadratic and oscillatory, with a single model-specific scalar amplitude. Within each model: `a ~ N(1, 0.25)` and observations satisfy `y_i | a,m ~ N(a phi_m(x_i), sigma_i²)` with *known, independent* Gaussian observation noise. Equal initial model weights. Neither an experimental instrument, physical calibration, nor real materials are tested.

## Independent analytical derivation

For one model and n observations, let prior mean `m0`, variance `v0`, feature `phi_i`, noise sd `sigma_i`, and define:

- `A = 1/v0 + Σ phi_i²/sigma_i²`
- `B = m0/v0 + Σ phi_i*y_i/sigma_i²`
- `C = m0²/v0 + Σ y_i²/sigma_i²`

Completing the Gaussian square yields posterior `a | D,m ~ N(B/A,1/A)` and the integrated log model evidence:

`log p(D|m) = -0.5 * [n log(2π) + Σ log(sigma_i²) + log(v0*A) + C - B²/A]`.

Unlike the production algorithm's sequential `Belief.update`, the audit computes these values directly from fixed observations as **batch sufficient statistics** and compares posterior means, variances, model weights and integrated evidence. This checks mathematical consistency under shared assumptions, not an entirely different probabilistic model.

## Independent EIG reference

The production method estimates model-index mutual information using equal-probability midpoint normal quantiles. The separate reference computes:

`I(M;Y|D,x) = Σ_m p(m|D) ∫ p(y|m,D,x) log[p(y|m,D,x)/p(y|D,x)] dy`.

Integration is deterministic midpoint quadrature over a union of per-model predictive ranges `μ_m ± 10σ_m`; 4001 grid bins on a fixed development example, versus 16/64/128 normal quantiles. It does *not* use `Belief.update` or production `information_gain` to compute the reference integral. Boundaries are finite and truncation/resolution remain approximations, not a proof of arbitrary precision.

## Checks and limitations

- Direct batch Gaussian posterior, integrated model evidence, model probabilities, mixture log density.
- Numerical EIG reference, quantile convergence and integration-grid refinement on a *developer-known* fixture.
- Zero-information point x=0; invalid observation variances and invalid integration parameters.
- `scored_validation_allowed=false`, `independent_holdout_used=false`, `claim_of_superiority=false`, `physical_validation=false`.
- No benchmark generator, no independent holdout seeds 10000..10099, no claims that model likelihoods represent genuine physical measurements.
- This numerical reference is independent **at the level of computation**, not independently replicated or reviewed by another institution. Cross-implementation agreement can still share incorrect modeling assumptions.

## How to run

```bash
python -m unittest discover -s tests -p 'test_independent_math_verification_v1.py' -v
python -m scripts.independent_math_verification_v1
```

## Publication decision gate

If the batch evidence or EIG comparisons fail, correct the computational methods before any full benchmark. Passing these fixed checks alone does **not** enable a publication claim or independent holdout. A future frozen protocol needs richer model classes, model misspecification treatment, strong external baselines, real licensed laboratory data, and external review.
