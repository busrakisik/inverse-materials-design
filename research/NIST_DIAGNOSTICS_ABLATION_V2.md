# BHS — NIST Anonymous Kerr Diagnostics & Ablation v2

**Status:** Post-hoc, retrospective, exploratory DEVELOPMENT ONLY. It is neither an independent evaluation nor scientific or physical validation. The independent BHS holdout seeds **10000–10099 are forbidden**. `scored_validation_allowed=false`.

## Scientific motivation and actual prior finding

The pinned NIST REMI Fe–Co–Ni dataset has 921 eligible experimental Kerr measurements in the v1 retrospective replay. Original v1 CI: https://github.com/busrakisik/inverse-materials-design/actions/runs/41977734103, artifact ID `13392975164`, commit `aaa70761cf97b8d5ed5360ed5991ac73669b746b`. In the already-explored three-seed (`7,13,23`), 15-measurement development campaigns, v1 measured average normalized final simple regret:

| Method | Development mean final regret (lower is better) |
|---|---:|
| GP Expected Improvement | 0.025001283117256388 |
| GP UCB | 0.07450292037487553 |
| BHS Bayesian Model Averaging EI | 0.13924593765076626 |
| Random | 0.19775608454202978 |

**These are not independent success, failure, or significant differences.** All follow-up ablations are deliberately proposed after seeing v1 results: they are *post hoc*. The first CI step reproduces the same v1 four-policy trajectories in unit tests on synthetic data, and the full real-data workflow compares the first three seeds' outcomes to the exact prior v1 artifact values (absolute tolerance 1e-9), failing if they differ. This protects against silent regressions; it does **not** make results independent.

## Single research question

**What modeling assumptions are responsible for the observed BHS–BMA–EI vs GP–EI gap in this real-data *property-optimization* replay?** We investigate response-family restriction, assumed observation noise, GP lengthscale and measurement budget, without changing the BHS's objective into a claim of physical hypothesis identification.

## Methods and fair comparison

All 11 methods receive the same anonymous `N×3` composition coordinates, fixed initial seed and its first three observed labels, same fixed per-campaign response normalization **using the first three labels only**, and **15 total acquisitions**. No policy receives hidden labels, a global maximum, per-candidate costs, or sample identities. Historical full-pool labels are used only by the retrospective evaluator after a policy selects an index. The v1 GP internally uses the first two simplex coordinates; the omitted third coordinate equals one minus their sum. The model families are generic mathematical *response shapes*, **not independently established Fe/Co/Ni physical mechanisms**.

| Condition | What it isolates |
|---|---|
| `random` | Uninformed policy |
| `gp_ei` | Original fixed-hyperparameter GP–EI (.22 coordinate lengthscale) |
| `gp_ucb` | Original fixed-hyperparameter GP–UCB |
| `bhs_bma_ei` | Original three-family BMA–EI (`sigma=0.15`) |
| `bhs_linear_ei` | Single linear response family (`sigma=0.15`) |
| `bhs_interaction_ei` | Single coordinate interaction family (`sigma=0.15`) |
| `bhs_localized_ei` | Single localized response family (`sigma=0.15`) |
| `bhs_bma_sigma_0p05` | BMA–EI with assumed `sigma=0.05` |
| `bhs_bma_sigma_0p30` | BMA–EI with assumed `sigma=0.30` |
| `gp_ei_length_0p12` | GP–EI with fixed lengthscale `.12` |
| `gp_ei_length_0p40` | GP–EI with fixed lengthscale `.40` |

The BHS prior parameter variance remains `0.5` in all cases; GP noise variance remains `.15²`; kernels have fixed hyperparameters, not optimized against labels. GP and BHS use **different model classes and priors**; this is an explanatory ablation, not a standardized equal-capacity benchmark. Noise values are **hypothetical on the per-campaign normalized response scale**, not laboratory-calibrated uncertainties. Acquisition assumes equal observation costs without measured cost evidence. The BHS mathematical basis called `fe_co_interaction` in v1 is used with **anonymous `source_col_0 × source_col_1`**, never asserted to correspond to Fe × Co.

Seeds `7,13,23,31,41` are all *development* seeds, never independent. Three were already explicitly seen in v1; two additional seeds are new development conditions, **not** an independent holdout. Five small, data-influenced replicates offer no publication-quality confidence interval or significance claim.

## What we report

- Final **normalized simple regret** at budgets 5, 10, and 15: `(global historical max − best observed so far)/(historical max − historical min)`. The evaluator alone reads the global max and range *after* selection. Results are per-policy **means, medians, minima, maxima and population standard deviations** across five development seeds.
- Paired per-seed **final-regret difference vs `gp_ei`** at budget 15, plus number of better/tie/worse development campaigns. These are descriptive, not statistical tests.
- BHS final model posterior **effective number of families** (`exp(Shannon entropy)`) and average posterior model weights: diagnostic for possible overconcentration, **not truth probability**.
- Reproduce v1's exact 3-seed means (4 original policies, artifact run pinned above); failure of this check blocks CI.

Artifacts contain **only aggregated results and test logs**, not raw NIST rows, material compositions, selected indices or per-step observation labels. Upstream NIST binary is fetched only at runtime from an immutable commit and checked for exact byte count plus Git blob hash by the existing source module. Do not commit or redistribute the source data until source-specific permission checks are complete.

## Critical interpretation and limitations

1. This is **retrospective optimization**, not prospective experiments, mechanistic materials discovery, or cost savings.
2. Source `C` column-to-element ordering and physical unit meaning are **not authoritatively verified**; anonymous coordinates only.
3. All 921 source rows have finite targets in the v1 eligible pool. A future dataset with missing outcomes needs a prospective missing-value and failed-experiment protocol. Even here, the evaluation pool is defined from historical observed availability.
4. Noise is arbitrary, independent and homoscedastic across samples; real instrument uncertainty and batch drift are unknown. No actual costs or batch information are used.
5. Model posterior weights depend heavily on selected hypothesis families, noise, response normalization and priors. A sharp posterior is not evidence for a physical mechanism.
6. This is **post-hoc model development**. We selected the diagnostic conditions after examining v1. No performance selection, statistical significance, independent holdout or validated superiority can be claimed.
7. Kernels in these GP references have fixed scales. A serious later benchmark requires tuned GP and calibrated, domain-supported alternatives with a frozen evaluation protocol.

## Reproducibility

```bash
python -m pip install numpy==1.26.4 scipy==1.13.1 scikit-learn==1.5.2
python -m unittest discover -s tests -p 'test_nist_diagnostics_ablation_v2.py' -v
python -m scripts.nist_diagnostics_ablation_v2 --fetch
```

For stable computational throughput on small GP linear algebra in CI, the job sets `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1` and `MKL_NUM_THREADS=1`; these are performance settings and do not change the dataset or development protocol.

Output: `runs/nist_diagnostics_ablation_v2/aggregated_diagnostic_ablation.json` and `.sha256` checksum file; CI also retains `nist_diagnostics_ablation_tests.log`.

Expected metadata: `development_only=true`, `post_hoc_model_diagnostics_not_pre_registered=true`, `scored_validation_allowed=false`, `independent_holdout_used=false`, `physical_validation=false`, `claim_of_superiority=false`, no raw rows. A failing v1 reproducibility assertion is an investigation trigger, not something to bypass by weakening the tolerance.

## Research decision after CI

Inspect whether BHS's family-specific EI variants beat its BMA combination on matched seeds, whether changing *hypothetical* sigma reverses rankings, and whether GP kernel scales materially change its outcome. Keep both gains and regressions visible. If BHS remains consistently behind GP for retrospective property optimization, **do not tune against this dataset indefinitely**. Recenter BHS's proposed scientific contribution on supported hypothesis selection and meaningful cost/uncertainty-aware experimental decisions, with a separate dataset and frozen independent protocol only after feasibility and expert review.

NIST primary scientific reference: Wang et al., *Benchmarking Active Learning Strategies for Materials Optimization and Discovery* (2022), https://www.nist.gov/publications/benchmarking-active-learning-strategies-materials-optimization-and-discovery. Their reported GP–EI performance motivates using GP–EI rather than an artificially weak baseline. Cite Wang et al. and Yoo et al. when working with the NIST data as requested by their source description.
