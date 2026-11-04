# BHS — Parametric Competing Hypotheses v2

**Development-only mathematical prototype. NO scored validation, NO holdout, NO physical materials discoveries.**

## Why this exists
The existing v1 assumes three fixed, known functions. v2 distinguishes three **families** with
one unknown scalar amplitude per family, rather than assuming exactly known curves.
Every observation records a known **standard deviation**, not an unverified reliability score.

## Mathematical contract
For model `m` in `{linear, quadratic, oscillatory}`:
- `phi_m(x)` in `{x, x², sin(3x)}`, `x` in `[-1,1]`;
- `a_m ~ Normal(1, tau²)`; default `tau² = 0.25`;
- `y_i | a_m, m, x_i, sigma_i ~ Normal(a_m phi_m(x_i), sigma_i²)`;
- Prior model probabilities are equal (configurable internally via `Belief.initial`).

Conditional on each model, the exact conjugate Gaussian update for amplitude is performed.
Evidence for model probabilities uses the **marginal posterior predictive** normal density,
which integrates parameter uncertainty:
`Var(y|m,D,x) = sigma² + phi_m(x)² Var(a_m|D)`.
This avoids the mathematically incorrect plug-in-likelihood update.

The one-step expected information gain (mutual information between model ID and
next observation) is estimated with deterministic midpoint normal-quantile integration.
There is a quadrature error; values are not exact guarantees. Unlike v1, both
candidate-specific planned standard deviations and observation-specific historical
standard deviations are supported.

`predictive_log_score` is a basic posterior predictive surprise diagnostic. It is not a
calibration test, out-of-family detector, or evidence that stated standard deviations are correct.

## Scientific limitations and potential failure cases

1. **Each model has only one scalar parameter.** This does not yet represent realistic
   multivariate physical hypotheses or unknown noise covariance.
2. **The three families may all be wrong** or observationally indistinguishable.
   Bayesian model probabilities are conditional on the assumed set; very high posterior
   probability does NOT establish physical truth.
3. Stated `sigma_i` values are assumed known, independent Gaussian measurement errors.
   The code does not calibrate reliability or defend against fabricated uncertainty values,
   batch effects, shared biases, correlated data, or adversarial evidence.
4. EIG optimizes model identification, *not* physical fitness or best-observed utility.
   Comparing its raw objective with earlier simple-regret experiments would be misleading.
5. The demonstration uses explicit fixed public candidates, private generating parameter
   `a=0.8` under quadratic family, and local RNG seed 17. It **does not call `make_task`**,
   create benchmark tasks, or use holdout seed range 10000..10099.
6. The development-only code is evaluated in-process. It is not an OS sandbox.
7. CI passing means software tests pass, not scientific validity or publication readiness.
8. No superiority claims; no independent confirmatory experiment; `scored_validation_allowed=false`.

## Commands

```bash
python -m unittest discover -s tests -p 'test_competing_hypotheses_v2.py' -v
python -m scripts.competing_hypotheses_v2
```

Outputs in `runs/competing_hypotheses_v2/` include a deterministic JSON development trace
and its SHA-256 checksum.

## Necessary next steps
- Cross-check marginal likelihood and EIG against an independent implementation.
- Test posterior predictive calibration and misspecification with a *development-only*
  protocol and external review; explicitly include out-of-family mechanisms.
- Replace a single amplitude with richer, identifiable parameterizations and controlled
  uncertainty estimates.
- Incorporate scientifically grounded measurement provenance, costs, batch effects,
  and common-mode noise only after careful interface design.
- Freeze model objectives and validation protocol **before** any future independent tests.

## Relationship to literature
Conjugate Bayesian linear modeling, Bayesian model comparison, and one-step EIG are
established mathematics. v2 is a useful research implementation, not a new
general-purpose discovery algorithm by itself.
