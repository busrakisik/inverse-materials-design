# BHS — Model Misspecification Stress v1

**Exploratory synthetic stress diagnostics. No holdout, no formal error control, no real material results.**

## Purpose and scientific question
The BHS v2 hypothesis model uses only three one-amplitude families (`linear`, `quadratic`, `oscillatory`) with independent, known Gaussian noise. This study asks how prequential predictive diagnostics behave when those **assumptions are intentionally violated**, without claiming to certify model inadequacy.

## Protocol
Fixed candidate descriptors at 24 sites in [-0.96,0.96]. Fixed development-only RNG tokens are distinct from benchmark task seed identifiers. In all six scenarios the **reported** observation standard deviation is 0.12:

1. `in_family`: quadratic amplitude 0.8 + correctly specified Gaussian measurement noise.
2. `underreported_noise`: same response but actual sigma 0.36; model is told 0.12.
3. `systematic_bias`: added constant 0.65, absent from all modeled parameterizations.
4. `gradual_drift`: additive bias ramps from 0 to 0.8 by observation order.
5. `out_of_family_step`: discontinuous sign step not representable by assumed smooth families.
6. `heavy_tailed_noise`: deterministic periodic high-variance contamination (every sixth point).

All cases share the same fixed public descriptors and input order. Scores and predictive 90% intervals are computed **before** the current outcome enters the model, by the existing `prequential_audit()` code. Reports contain empirical coverage, coverage gap, mean negative log predictive density, mean PIT, fraction of PIT values in outer 5% tails, two half-stream summaries and final maximum model probability.

## Interpretability / restrictions
- These six examples were selected by developers **after** studying limitations and are therefore not an independent validation of anomaly detection or classifier sensitivity/specificity.
- 24 outcomes per scenario are insufficient to infer general coverage. Prequential scores are path/order-dependent. Comparisons are **descriptive**, with no p-values, arbitrary warning thresholds or formal out-of-distribution detector.
- Calibration of declared measurement uncertainty is not performed. Models can become highly confident while being wrong. A low coverage alone is not proof of a particular root cause.
- Different synthetic mechanisms intentionally depart from the model in multiple ways (noise or mean). There is **no causal attribution guarantee** from diagnostic summaries.
- Inputs contain no materials, private benchmark labels or independent validation seeds 10000..10099. `make_task()` is never called. `scored_validation_allowed=false`.
- The evaluation executes trusted Python in-process; no security sandbox implied.

## Execute
```
python -m unittest discover -s tests -p 'test_misspecification_stress_v1.py' -v
python -m scripts.misspecification_stress_v1
```

Results: `runs/misspecification_stress_v1/stress_report.json`, matching SHA-256 file. For future work, preregister an independently reviewed detector specification and benchmark design **before** any confirmatory evaluation.
