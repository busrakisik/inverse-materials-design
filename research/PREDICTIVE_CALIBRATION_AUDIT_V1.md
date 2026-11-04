# BHS — Prequential Predictive Diagnostics v1

**Exploratory synthetic developer diagnostic, not a certified calibration test. No holdout.**

## Aim
Test the failure modes of `scripts/competing_hypotheses_v2.py` when the assumed model set does not contain the data-generating mechanism. The decision rule does not infer that one model is *true* merely because its posterior probability is high.

## Protocol
- Two fixed, deterministic, transparent illustrative data streams at twenty predefined candidate locations, not benchmark seeds: quadratic amplitude 0.8 (inside family) and discontinuous sign step (outside all three smooth model families).
- Known and fixed illustrative Gaussian measurement standard deviation of 0.12; this does not demonstrate real evidence calibration.
- For each stream and each candidate in chronological order, compute the **posterior predictive** central 90% mixture interval, probability integral transform (PIT), and negative log predictive density **before observing** its value; only then update the model posterior.
- Summarize empirical coverage, mean PIT and mean negative log predictive density. Include posterior maximum probability as an *overconfidence diagnostic*, not a correctness score.
- Source code uses the exact v2 mixture predictive with within-model parameter uncertainty. We do not use plug-in point estimates for the interval.

## Important limitations
1. These two demonstrations are developer-chosen examples; with only 20 sequential points, empirical coverage is noisy. No calibration, robustness, or out-of-family sensitivity/specificity claim is justified.
2. The out-of-family generator is deliberately discontinuous and was selected after understanding the model family. This is not independent validation.
3. Fixed candidate order is not the EIG policy; the purpose is evaluating **prequential forecasts**, not demonstrating experiment-selection superiority.
4. The score may flag surprises even if all model probabilities concentrate, but no formal misfit threshold or detector has been validated.
5. Known Gaussian, independent observation errors remain an assumption. Shared bias, measurement drift and variance estimation are not implemented.
6. The test module runs trusted in-process code; no untrusted worker protection is established.
7. `scored_validation_allowed=false` for all outputs. Holdout seeds 10000..10099 are never generated or used.

## Run

```
python -m unittest discover -s tests -p 'test_predictive_calibration_audit_v1.py' -v
python -m scripts.predictive_calibration_audit_v1
```

## Next
Independent mathematical verification of predictive log scores and mixture-quantile accuracy; larger **development** experiments and robustness checks without touching holdout. Any proposed future formal detector needs an explicit predeclared error-rate target and independent review before confirmatory use.
