# BHS Bayesian-only synthetic policy v1 — contract milestone

**NOT_SCORED / SYNTHETIC_ONLY / NO_MATERIALS_CLAIMS / NO_MCTS / NO_REAL_ORACLE**

This is a minimal, genuinely Bayesian acquisition policy using a single-weight Gaussian linear model, sequential posterior updates from previously queried candidate values and seeded Thompson-like sampling. The choice is made from a draw of the posterior coefficient. It integrates with `MeteredEvaluator` in `scripts/scientific_benchmark_contract_v1.py` and does not read the evaluator's hidden label mapping.

### Model and deliberate limitations

Public descriptor `x` is scalar. Prior `w ~ N(0, sigma_prior^2)`, observation noise `y | w,x ~ N(w*x, sigma_noise^2)`. Posterior variance `1/(1/sigma_prior^2 + sum(x^2)/sigma_noise^2)` and posterior mean `variance * sum(x*y)/sigma_noise^2`. The policy samples a weight and maximizes sampled utility `w*x`. This is NOT a general scientific hypothesis generator, Bayesian model comparison, calibrated evidence model, actual MCTS/PUCT or physical materials discovery; nonlinearity, noise mismatch and constant descriptors are deliberate stress cases.

### Gates and next steps

13 deterministic contract tests check updates, finite input, unique query selection, seeded repeatability and integration with five synthetic generator scenarios. Tests DO NOT constitute a scored empirical comparison. The fixed parameters are prototype defaults, not tuned/frozen experimental settings. Before any scored comparison: resolve generator provenance/hash, independently audit labels/public separation and threat model, freeze policy and baseline versions, set seeds without test-driven tuning, validate uncertainty calibration and distinguish synthetic development data from an independently held-out test set. Never claim superiority from these CI tests. Preserve previous contract test modules and branches. Do not merge to main or release Zenodo yet.
