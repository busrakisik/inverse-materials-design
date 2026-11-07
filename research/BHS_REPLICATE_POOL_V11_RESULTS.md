# BHS v11 — Negative result from a genuine historical three-replicate mechanical benchmark

**7 November 2026 — completed source-pinned, paired, retrospective DEVELOPMENT study.**

**Conclusion:** The inherited BHS v5 *statistical kernel-portfolio EI component* did **not** outperform a strong optimized anisotropic Gaussian-process reference (**GP–ARD EI**) on mean final retrospective regret. It also fell slightly behind an RF-UCB heuristic. Results were committed without post-result tuning or changing the preregistered comparison.

This study evaluates **only that existing BHS statistical kernel component** on a different empirical task, not the full hypothesis-centric architecture, a physically validated competing scientific hypothesis set, an adaptive MCTS experiment scheduler, or real laboratory value.

## Original physical observations and fixed protocol

Source-authorized historical 3D-printed crossed-barrel toughness measurements from Gongora et al. (2020), *Science Advances* 6, eaaz1708, DOI [10.1126/sciadv.aaz1708](https://doi.org/10.1126/sciadv.aaz1708), shared in Liang et al. (2021), *npj Computational Materials* 7, 188, DOI [10.1038/s41524-021-00656-9](https://doi.org/10.1038/s41524-021-00656-9).

Public `PV-Lab/Benchmarking` repository, exact source Git commit `7585c517ad88e676c42c6bf24a8ad278e01ddb21`; Git blob `b007fe5d8762233bbd23c8cf83858b169f05492a`; source raw CSV SHA-256 `2c01f875f3c210e986ca6142bf20f417884c2ad7d6f008c2fc574b44a3d5f606`. Source files were not redistributed. The source contains **600 distinct designs with 3 historical physical repetitions each** (1,800 source responses). **BHS did not perform any new physical experiment.**

The [v11 protocol](BHS_REPLICATE_POOL_V11_PREDECLARED_PROTOCOL.md) was committed **before running any v11 selection outcome**. It fixed five *already-explored development seeds* `7,13,23,31,43`, shared **6 initial designs** and **10 further distinct geometries** per method. Selecting a geometry reveals **all 3 previously measured values**, so each campaign observes exactly **16 geometries / 48 historical measurement responses**.

Methods:
- **random** selection, distinct geometries without replacement.
- **GP–ARD EI:** 4D Matérn-5/2 GP, marginal-likelihood-optimized independent ARD lengthscales, with estimated training-noise diagonal from **only acquired triplicates**. Its estimated noise is not calibrated laboratory uncertainty.
- **RF–UCB:** a 160-tree random forest with a mean-plus-tree-spread heuristic acquisition; tree spread is **not a probabilistic confidence bound**.
- **Existing BHS v5 kernel-portfolio EI:** the unchanged `scripts.uci_concrete_v5.choose_next` implementation, using the acquired geometry means and fixed two-kernel statistical portfolio. Statistical kernel families are **not** competing physical scientific hypotheses.

Candidate descriptors are publicly visible; only the acquired triplicates become visible to each selector. The full pool mean optimum enters the evaluator **after** acquisition to compute retrospective simple regret. No selected design ID, raw response row or private oracle value is committed.

## Results — published without adapting to outcomes

**Primary metric:** final simple regret (J), calculated as the maximum **historical observed triplicate mean** across the 600-design pool minus the maximum **historical observed triplicate mean** among the 16 acquired designs. Lower is better. This is a *noisy historical empirical reference*, **not** the physically true latent optimum.

| Method | Mean final regret (J) | Mean normalized regret | Found a top-decile observed-mean design |
| --- | ---: | ---: | ---: |
| **GP–ARD EI** | **7.363** | **0.1591** | 5 / 5 seeds |
| RF–UCB | 8.983 | 0.1941 | 4 / 5 seeds |
| BHS v5 kernel-portfolio EI | 9.368 | 0.2024 | 5 / 5 seeds |
| Random | 15.951 | 0.3447 | 3 / 5 seeds |

Each method had the exact same **16 geometry / 48 historical measurement** budget per seed. The average of five repeated development campaigns does **not** justify confidence intervals, statistical significance, broad generalization or a scientifically proven superiority claim.

### All paired development seed outcomes

| Seed | Random regret (J) | GP–ARD EI regret (J) | RF–UCB regret (J) | BHS portfolio regret (J) |
| --- | ---: | ---: | ---: | ---: |
| 7 | 16.763 | 10.243 | 14.440 | 12.237 |
| 13 | 11.753 | 8.505 | 1.767 | **3.384** |
| 23 | 15.726 | 7.790 | 16.910 | 11.515 |
| 31 | 13.122 | 5.138 | **0.000** | 12.237 |
| 43 | 22.390 | 5.138 | 11.797 | 7.469 |

The existing BHS kernel portfolio beat GP–ARD on **one seed (13)**, and was worse on **four**. RF–UCB outperformed GP–ARD on two seeds (13, 31) but had more variable development outcomes. BHS outperformed random on average, **but not** either of the two reference methods. The 'any top-decile design' measure **does not discriminate well**: BHS and GP–ARD both scored 5/5, despite an important difference in actual regret.

### Transparent magnitude

- BHS mean regret is **2.005 J higher** than GP–ARD (about **27.2% of GP–ARD regret** in this particular development sample).
- BHS mean regret is **0.385 J higher** than RF–UCB.
- BHS mean regret is **6.583 J lower** than random; this is a descriptive development comparison, **not** a proven improvement in physical decision safety.
- The dataset's best *recorded triplicate mean* is about **46.71 J**. Its sample average is **not** a calibrated ground-truth optimum and was not available to the selector.

These differences vary substantially across seeds. No post-hoc hyperparameter optimization or second-choice subset of this dataset can be counted as independent confirmation.

## Why this result matters scientifically

**1. The old portfolio alone has not established an advantage.** A Gaussian-process baseline with learned anisotropic scales does better here. Combined with earlier NIST and UCI development results, there is no defensible evidence that simply averaging statistical families is the scientific innovation. We should be willing to falsify the initial approach rather than indefinitely change hyperparameters until we see a favorable result.

**2. Robust experimental design matters more than cosmetic benchmarks.** v10 demonstrated that random response-row splits place **92.4%** of test rows at geometries already in training. v11 acquires **whole geometries with all repeats**, with strict label isolation and budget parity.

**3. Repeatability remains a real scientific uncertainty.** Three experimental responses per geometry are available, but process/batch/printer provenance is absent. GP's response-variance plug-in is a modeling assumption; neither GP's posterior nor RF's tree spread is demonstrated to be physically calibrated. The RF, GP and portfolio exploit acquired repeats differently, so these results do **not** isolate the causal contribution of replicate-noise modeling.

**4. More restrictive laboratory recommendations must be earned.** v11 does not yet evaluate risk-aware abstention or value-of-information for additional replicates. Before the system can recommend real physical interventions, it needs domain experts, independent experimental outcomes, a predeclared loss model, and comparisons at **matched decision coverage**.

## Reproducibility

- [Pre-run protocol](BHS_REPLICATE_POOL_V11_PREDECLARED_PROTOCOL.md)
- [Implementation](../scripts/bhs_replicate_pool_v11.py) and [13 acquisition/label-isolation tests](../tests/test_bhs_replicate_pool_v11.py)
- [Exact, first-run source-locked development JSON](bhs_replicate_pool_v11.json) (no raw source responses or selected IDs).
- GitHub Actions [first real-data run **42347524338**](https://github.com/busrakisik/inverse-materials-design/actions/runs/42347524338), success; 13 v10 + 13 v11 contracts passed.
- [Exact byte-checked archive run **42347679129**](https://github.com/busrakisik/inverse-materials-design/actions/runs/42347679129), success; source aggregate SHA-256 `75be43b53e734f6fb54dc82154022ee315a76e1c0891727fd7e8fddcd1378db8`, verified against the original first-run output.

## Evaluation boundaries and next target

`development_only=true`, `scored_validation_allowed=false`, `independent_holdout_used=false`, `physical_validation_by_bhs=false`, `causal_identification=false`, `claim_of_superiority=false`, `real_savings_measured=false`, and NIST protected seeds `10000..10099` remain unused.

**Next research design question:** Instead of adding more statistical kernels, can we define a falsifiable, risk-sensitive **value of replication versus exploring a new geometry** under a truly fixed *physical measurement budget*? The current dataset has only three recorded repeats per geometry and unknown batch dependence; a retrospective policy that chooses repetitions must explicitly account for those source limits, avoid reusing unrevealed outcomes, and must not claim new physical experiments or validated cost savings. A separate independently controlled prospective laboratory test remains necessary for a doctoral-grade generalization claim.
