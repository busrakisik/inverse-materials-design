# BHS — NIST Kerr Prequential Model Adequacy & Uncertainty v3

**Status: post-hoc, retrospective, adaptive *development* on already-explored data. NOT independent validation, physical mechanism identification or calibrated measurement uncertainty.**

## Why now? Grounded v2 finding

The verified NIST Kerr ablation v2 CI run **41988359209** (commit `3a6762c7a5de1ecab7587ab1b938108bb5d9f8f5`, artifact `13397435952`) passed 28/28 tests and compared 11 policies × 5 already-development seeds × 15 observations. The aggregate results are published in its attached artifact, not raw NIST rows. Observed developer-only mean final normalized regret: GP–EI fixed .22 lengthscale **~0.0150**, BHS–BMA–EI nominal sigma .15 **~0.08355**, BHS–BMA nominal sigma .05 **~0.05391**, GP–EI lengthscale .40 **0.0**. This motivated asking whether uncertainty and predictive fit are scientifically adequate. *The .40 and .05 choices are post-hoc; do not present as independent improvements.*

## Research question

**Under the *same* adaptively selected measurement histories, how do five fixed predictive models compare in one-step-ahead predictive log density, RMSE, coverage and interval width?** This is model adequacy, not acquisition superiority. Each model has its own prior/noise assumptions. Comparing the five models on the *same trajectory* isolates the prediction component from its acquisition-policy path. Repeating across three trajectories checks dependence on the selection mechanism; it does not produce independent confirmation.

## Data, metadata, and leakage boundary

- Source binary: NIST REMI `usnistgov/remi`, immutable commit `596b04435fb577175264a70c4434f5539b809510`, Git blob SHA-1 `e506db115d522d62618042abead7df2695ccf13e`, 289480 bytes. Existing `fetch_source()` and `validate_source()` from `nist_dataset_inspection_v1.py` enforce this. Real `.mat` content is fetched **only** by CI with explicit `--fetch`; never committed or uploaded.
- Data task: **Kerr (mrad)**, N=921 eligible historical measurements in the previously confirmed retrospective sample pool. The candidate eligibility criterion uses historical target availability, so this is not a prospective failed-measurement benchmark.
- Coordinates remain anonymized as `source_col_0,1,2`; no physical Fe/Co/Ni order, fraction/percent provenance or sample-specific measurement error is certified.
- Development seeds **(7,13,23,31,41)**, all previously used in v2; independently reserved BHS seeds **10000–10099 are PROHIBITED**.
- Three *fixed acquisition histories*: `random`, `gp_ei` (lengthscale .22), `bhs_bma_ei` (sigma .15). At each seed, policy gets the same initial 3 observations and uses the existing v1 `choose_next()` API; there are **15 total acquisitions**. Only 12 subsequently chosen measurements are used for *prequential* forecasts.
- For each candidate selected by a policy, **all five predictive models forecast BEFORE the label is revealed**. The selected label is revealed only inside the evaluator and used to score the forecasts, then incorporated into the next step's observed history. The model-forecast API receives `candidates`, `selected`, `observed_z` and a `candidate_index`, not the hidden label vector.
- Per-campaign response normalization is computed exclusively from the first three already-observed values and held fixed. Consequently scoring is in a *per-campaign standardized response scale*, not mrad and not directly comparable to independently measured instrument noise. Comparisons are paired *within* trajectory and seed.

## Five predictive variants (not physical theories)

| Predictor | Assumed/selected modeling settings | Provenance |
|---|---|---|
| `gp_length_0p22` | GP RBF length .22, alpha .15², no optimization | Original v1 baseline, fixed |
| `gp_length_0p40_posthoc` | GP RBF length .40, same assumed alpha | Chosen in v2 ablation *after* seeing v1 |
| `bhs_bma_sigma_0p15` | Three phenomenological Gaussian-linear families, prior variance .5, nominal noise .15 | Original v1 BHS |
| `bhs_interaction_sigma_0p15` | Only coordinate_0 × coordinate_1 mathematical family | Post-hoc v2 ablation; NOT Fe–Co mechanism |
| `bhs_bma_sigma_0p05_posthoc` | BHS family mixture, assumed noise .05 | Post-hoc v2 noise sensitivity; NOT calibrated |

GP Gaussian predictive variance is *latent* GP variance **plus nominal observation variance `.15²`**. The BHS model predictive variances already include the nominated Gaussian observation variance. The BHS-BMA posterior is a **Gaussian mixture**, not necessarily one Gaussian: predictive intervals are computed by numeric inversion of the actual mixture CDF; NLPD uses the correctly weighted log-sum-exp over family densities. Family model weights only express preference under assumed candidate bases and priors, **not probability of a true materials mechanism**.

## Actual diagnostics in the aggregate report

For each of **3 selection histories × 5 predictor models**, 5 developer seeds × 12 prequential one-step forecasts = **60 predictions** per cell, **900 total**. The program never publishes per-step selected indices, labels, compositions, predictions or sample identities. Report only:

1. Mean **negative log predictive density** (NLPD; lower is better), calculated on the standardized observed outcome and each observation-level predictive distribution. *Differences* are paired within seed and acquisition history against original GP .22.
2. Mean per-seed prequential RMSE and MAE in standardized response units (lower is better); the report says explicitly `mean_rmse`, not pooled global RMSE.
3. Empirical **90% predictive interval coverage**, mean interval width and the fraction outside ±2 predictive SD; distinguish apparent under/over-coverage from true instrument uncertainty calibration.
4. Five-bin probability integral transform (PIT) histogram as counts (not raw PIT values). With 60 adaptively sampled, dependent observations, a coarse diagnostic only.
5. Per-seed paired NLPD better/tie/worse counts relative to GP .22, *descriptive only*.

Different acquisition histories sample different parts of the surface, therefore avoid claiming that lower NLPD on the **GP–EI trajectory** proves an intrinsically better model everywhere. This is *adaptive observational* prequential scoring; the dataset and model choices have already been examined in v1/v2. No statistical significance, independent replication, publication-quality uncertainty intervals, superior material discovery or cost claim is warranted.

## Verifications / fail-closed rules

- **31 synthetic-only tests**, including known Gaussian mixture density, true mixture quantiles, posterior alignment, v1 GP prediction parity, matching v1 trajectory selections, 12 forecasts per trajectory, observed-only API, distinct and safe development seeds, deterministic aggregate, no raw rows in output.
- CI checks exact synthetic test count, immutable source integrity, NIST eligibility 921 on the pinned file, **3 histories × 5 models × 5 seeds** and **60 forecasts per cell**, all finite metrics, PIT bin counts, safety flags and aggregate-only artifact contents.
- Source byte SHA-256 is logged for provenance. No raw data or per-index outcomes in GitHub artifacts. In source code, tests may operate on synthetic arrays; these are not real NIST labels.
- **No independent seeds 10000–10099.** `scored_validation_allowed=false`, `independent_holdout_used=false`, `physical_validation=false`, `claim_of_superiority=false`.

## Reproduce

```bash
python -m pip install numpy==1.26.4 scipy==1.13.1 scikit-learn==1.5.2
python -m unittest discover -s tests -p 'test_nist_model_adequacy_v3.py' -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -m scripts.nist_model_adequacy_v3 --fetch
```

Output (aggregate only): `runs/nist_model_adequacy_v3/aggregated_prequential_adequacy.json`, `.sha256`; workflow archives these and test log, **not** source data.

## Scientific decision after CI

Interpret matched NLPD, RMSE and interval coverage by trajectory. If BHS is overconfident (severe NLPD/coverage failures), investigate likelihood misspecification and empirical heteroscedasticity instead of assuming a physical discovery. If single-family interaction outperforms BMA on prequential prediction, revise or retire inappropriate phenomenological families *only as exploratory model development*. If no predictive gains vs GP, be prepared to reject BHS as a better general-purpose Kerr optimizer and focus on a domain-reviewed question about hypothesis discrimination rather than chasing post-hoc parameter choices. Before a manuscript claim, acquire genuinely different data or a properly isolated, pre-declared evaluation with domain approval.

## Required upstream scientific citations

Wang et al. (2022), *Benchmarking Active Learning Strategies for Materials Optimization and Discovery*, doi:10.1093/oxfmat/itac006; Yoo et al. (2006), *Identification of amorphous phases in the Fe–Ni–Co ternary alloy system using continuous phase diagram material chips*, *Intermetallics* 14, 241–247. See NIST source description: https://github.com/usnistgov/remi/blob/nist-pages/data/Combinatorial%20Libraries/Fe-Co-Ni/data%20description.txt.
