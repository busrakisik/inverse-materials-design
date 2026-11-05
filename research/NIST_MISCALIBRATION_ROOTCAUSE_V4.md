# BHS — NIST Kerr Predictive Miscalibration Decomposition v4

**Scientific status: post-hoc, retrospective, adaptive DEVELOPMENT ONLY.** This is an uncertainty-decomposition diagnostic, **not causal identification of an error source, fitted recalibration, independent validation, or evidence of a physical mechanism**. The independent BHS holdout seeds **10000–10099 are forbidden**. Always keep `scored_validation_allowed=false` and `physical_validation=false`.

## Verified motivation and source of the frozen comparison

The previous NIST Kerr prequential adequacy experiment **v3** completed successfully on GitHub Actions run [41992614426](https://github.com/busrakisik/inverse-materials-design/actions/runs/41992614426), commit `c6ea12510218bf4490dc637408df9de3d8fb8eb6`, artifact `13397919991`. It passed **31/31** tests and produced **900** one-step-ahead predictions across **3 acquisition histories × 5 forecasters × 5 previously used development seeds × 12 steps**. The v3 report's SHA-256 checksum was verified. Its original GP `.22` and BHS–BMA `sigma=.15` **90% predictive interval coverages** were, respectively:

| Adaptive acquisition history | GP .22 | BHS–BMA .15 |
| --- | ---: | ---: |
| Random | 0.4333 | 0.2833 |
| GP Expected Improvement | 0.4333 | 0.1667 |
| BHS–BMA Expected Improvement | 0.4833 | 0.3333 |

Both models undercovered on these adaptively sampled, previously examined development trajectories. This is **not** a classical test-set calibration estimate, a statement about instrument noise, or a demonstration of a general statistical significance level. The v3 NLPD values are stored at full precision inside the v4 `V3_PARITY` regression reference; these values are used only to ensure **reproduction of the same existing forecasts**, not to choose a new model.

## Precise research question

**Can the low predictive-interval coverage be described by insufficient assumed observation variance, insufficient within-model uncertainty, model-family disagreement, novelty of newly selected compositions, or systematic signed residuals?** These categories are nonexclusive descriptive diagnostics. In particular, aggregating model variances does **not** identify which unobserved physical process caused a forecast error.

## Mathematically correct predictive variance decomposition

For a Gaussian mixture with family weights \(w_m\), means \(\mu_m\), and conditional **observation-level** variances \(v_m\), define \(\bar\mu=\sum_m w_m\mu_m\). With an explicitly *assumed* common nominal noise variance \(\sigma_0^2\) for each model family:

\[
\operatorname{Var}(Y\mid D) = \underbrace{\sigma_0^2}_{\text{assumed noise}} + \underbrace{\sum_m w_m(v_m-\sigma_0^2)}_{\text{within-family / latent uncertainty}} + \underbrace{\sum_m w_m(\mu_m-\bar\mu)^2}_{\text{between-family disagreement}}.
\]

For the one-component GP this reduces to nominal observation variance + latent GP predictive variance, with the between term zero. For a single BHS interaction family, the between term is also zero. For BHS–BMA, family disagreement is between **chosen generic mathematical response shapes**, NOT confirmed physics mechanisms. The code checks the direct mixture variance identity and rejects components whose predictive variance is smaller than nominal noise.

## Non-causal diagnostic experiments

- **Paired prequential forecasts:** 3 unchanged acquisition histories (`random`, `gp_ei`, `bhs_bma_ei`) × 3 unchanged predictors (original `gp_length_0p22`, `bhs_bma_sigma_0p15`, and post-hoc `bhs_interaction_sigma_0p15`) × 5 **already-explored** seeds `(7,13,23,31,41)` × 12 forecasts = **540 predictor–observation scores**. Each method forecasts before the newly selected label is revealed. All predictions are in per-campaign standardized response units, normalized using the first three observed Kerr values only.
- **Residual and moment diagnostics:** mean signed residual, mean squared error, mean squared standardized error \(E[(Y-\bar\mu)^2/V]\), empirical MSE / mean predicted variance, NLPD, 90% interval coverage, and the three predicted variance contributions. These metrics are indicative, not formal calibrations in this adaptive setting.
- **Anonymous composition novelty:** Euclidean distance from a selected candidate to its nearest previously measured candidate in the *three anonymous normalized coordinates*; arbitrary predeclared descriptive bins: near `<0.08`, middle `[0.08,0.20)`, far `>=0.20`. Distances are not physical lengths, chemical similarities, or orthogonal causal treatments. Small/empty strata may yield unstable/missing estimates.
- **Acquisition phase:** first six vs last six forecasts after three initialization observations, indicating possible sequential degradation. These are not temporally independent replicates.
- **Post-hoc discrepancy sensitivity:** without refitting or changing choices, add an explicitly hypothetical \(\tau^2\) to every observation-level Gaussian component variance (\(\tau\) in standardized units: `0.0`, `0.5`, `1.0`, `2.0`), and recompute *exact mixture* 90% intervals and NLPD. **This is not fitted noise calibration** and does not make the measurement uncertainty known. Reporting improved post-hoc coverage does NOT authorize choosing \(\tau\) as a validated predictor or a deployment policy. We do not claim heteroscedastic noise has been established.
- **Parity with verified v3:** Reproduce the exact previously reported nine predictor × trajectory NLPD and coverage aggregate pairs within tolerance `1e-7`. Failure stops GitHub Actions. These metrics were collected from the verified v3 artifact and are not a new holdout.

## Source and independent evaluation restrictions

Data source: NIST REMI Fe–Co–Ni pinned commit `596b04435fb577175264a70c4434f5539b809510`, binary Git blob SHA-1 `e506db115d522d62618042abead7df2695ccf13e`, 289480 bytes. The source is verified by `fetch_source()` and `validate_source()` prior to use. Original NIST source data is fetched at runtime only; no raw binary, measured label, selected index, feature vector, or per-step residual is saved to GitHub artifacts. Only aggregated statistics are archived.

**The physical element order of `C` is still unverified.** The task is historical **Kerr property-prediction adequacy in anonymous composition space**, not physical Fe–Co/Ni interaction identification, a prospective physical experiment, or measured money savings. Instrument calibration and per-row standard deviations are unknown, nominal noise is a *modeling assumption*, and the user has not authorized raw NIST redistribution. The same development data have been inspected repeatedly, including selection of v2/v3 diagnostic alternatives; no scientific superiority claim is warranted.

## Read and run

```bash
python -m pip install numpy==1.26.4 scipy==1.13.1 scikit-learn==1.5.2
python -m unittest discover -s tests -p 'test_nist_miscalibration_rootcause_v4.py' -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python -m scripts.nist_miscalibration_rootcause_v4 --fetch
```

Expected local synthetic tests: **36/36**. Real GitHub CI results remain **unverified until the workflow runs**. Output is aggregate-only:

- `runs/nist_miscalibration_rootcause_v4/aggregated_rootcause_diagnostics.json`
- `runs/nist_miscalibration_rootcause_v4/aggregated_rootcause_diagnostics.sha256`

Workflow archives only the aggregate JSON, its checksum, and synthetic test log. It checks the 921-record real source pool, the 540 forecast count, six early/late bins per seed, novelty-bin count conservation, variance decomposition identity, fixed discrepancy scenarios, v3 parity, no labels in published reports, and all false-only claim gates.

## How to interpret; decision framework

1. High empirical squared error relative to mean predicted variance indicates inadequate predictive uncertainty **on these development trajectories**. It does not by itself isolate nominal noise from mean-model inadequacy.
2. High between-family disagreement indicates disagreement **within the three specified functional forms**; low between-family disagreement together with high errors may instead indicate all families are jointly wrong, or other forms of misspecification. The result cannot establish this distinction causally.
3. Large signed residuals, especially by early/late or novelty groups, may motivate a *separate predeclared study* of model bias or spatially varying error. The number of observations per group must be reported.
4. Increasing hypothetical discrepancy variance will mathematically widen intervals, which can improve observed coverage on the same data. That does **not** prove its variance value corresponds to laboratory measurement errors; excessive inflation sacrifices sharpness and can degrade NLPD.
5. This is already the **fourth investigation on the same Kerr data**. After interpreting this decomposition, stop tuning indefinitely; prioritize author confirmation of composition semantics, domain-supported hypotheses and an independent dataset or genuinely external scientific review before a publishable claim.

Upstream citations requested by the NIST source: Wang et al. (2022), *Benchmarking Active Learning Strategies for Materials Optimization and Discovery*, DOI `10.1093/oxfmat/itac006`; Yoo et al. (2006), *Identification of amorphous phases in the Fe–Ni–Co ternary alloy system using continuous phase diagram material chips*, *Intermetallics* 14, 241–247.
