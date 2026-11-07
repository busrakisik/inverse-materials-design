# BHS v11 — Predeclared replicate-aware materials acquisition development protocol

**Protocol committed 7 November 2026, BEFORE any v11 sequential acquisition scores or outcomes were computed.** Earlier v10 aggregate statistics have already been examined. This is **exploratory development**, NOT independent validation, a new physical experiment, or a prospectively registered study.

## Precise question

On an existing 600-geometry experimental pool, is the existing BHS v5 *statistical kernel-portfolio expected-improvement* selection policy competitive with a **strong anisotropic GP–ARD EI baseline**, a **Random Forest upper-confidence heuristic**, and uniform random acquisition when:

1. each candidate refers to **one distinct physical design**;
2. each acquisition reveals **all 3 previously measured outcomes** for that design, at a cost of 3 physical measurements;
3. all policies share exactly the same initial acquired designs and additional geometry budget; and
4. the policy cannot read a hidden design's outcomes, global optimum, or experimental replicate dispersion before acquisition?

**Scientific caution:** The inherited v5 portfolio is a mixture of *statistical kernels*, not competing independently validated mechanistic hypotheses. This is a fair test of the **existing software component's retrospective selection behavior** only. A win here would not establish causal hypothesis discovery, laboratory safety, or future industrial value.

## External source fixed before scoring

- Liang et al. (2021), *npj Computational Materials* 7, 188, DOI [10.1038/s41524-021-00656-9](https://doi.org/10.1038/s41524-021-00656-9); original Gongora et al. (2020), *Science Advances* 6, eaaz1708, DOI [10.1126/sciadv.aaz1708](https://doi.org/10.1126/sciadv.aaz1708).
- Public MIT PVLab benchmarking `PV-Lab/Benchmarking`, commit `7585c517ad88e676c42c6bf24a8ad278e01ddb21`, `datasets/Crossed barrel_dataset.csv`, immutable Git blob SHA-1 `b007fe5d8762233bbd23c8cf83858b169f05492a`. Exact source bytes verified by v10 parser. Software license MIT; credit original authors, do not mirror raw measurement table.
- Known from v10: 1,800 physical measurements, **600 unique crossed-barrel geometries, 3 repeats per geometry**. Reuse source only for development; earlier v10 measurements/summary were read and discussed. Never call a new split of this archive a newly untouched independent holdout.

## Frozen policies, budget and data visibility

**Five shared development seeds:** `7,13,23,31,43`; reserved independent seed IDs `10000..10099` are prohibited. Each seed chooses **six** initial geometry IDs uniformly without replacement and shares them across all policies. Each policy then chooses exactly **10** additional *unseen* geometry IDs. Total budget: **16 geometries, 48 previously measured response rows** per policy and seed, zero new laboratory experiments.

Input features: numerical design variables `n,theta,r,t`, standardized by the **unlabelled 600-design pool** only (a documented transductive pool setting). All policies see all candidate features, only the IDs of selected geometries, and exactly the acquired three responses per selected geometry, passed via a restricted acquisition view.

- **random:** uniform without replacement.
- **gp_ard_ei:** Matérn-5/2 Gaussian-process EI with **four independent ARD lengthscales** and marginal-likelihood hyperparameter optimization, initialization `1`, optimizer `fmin_l_bfgs_b`, `n_restarts_optimizer=0` (one fitted initialization), lengthscale bounds `[0.1,10]`, constant-amplitude bounds `[0.1,10]`. Diagonal `alpha` at selected geometries is the acquired triplicate sample-mean variance `s²/3`, standardized using observed `y` scale, clipped to `[1e-3, 1]`. These choices are *assumptions*, not instrument-calibrated variance. EI is applied to latent mean predictions.
- **rf_ucb:** RandomForestRegressor `n_estimators=160`, `min_samples_leaf=2`, `max_features=1.0`, `bootstrap=True`, `n_jobs=1`; choose the highest `mean + 1.0 * std` of predictions across trees, standardized to acquired labels. Tree spread is a heuristic ranking score, **not** calibrated posterior probability.
- **bhs_v5_kernel_portfolio_ei:** the **unchanged existing `scripts.uci_concrete_v5.choose_next`** implementation with `policy='kernel_portfolio_ei'` on the current four-dimensional standardized geometry descriptors and **acquired group means only**. Its two fixed kernel components and evidence weight rule are not altered or tuned after inspecting v11 results. Do **not** reinterpret these kernels as mechanical mechanisms.

All models use acquired group means. The GP also consumes measured dispersion already revealed for acquired geometries; the BHS port and RF ignore dispersion beyond the mean. This is a deliberate, documented policy-feature asymmetry, not a claim that the comparison isolates the scientific value of noise modeling.

**Acquisition-isolation contract:** the selector must have no argument containing the full target vector, reference best-known empirical mean, unseen triplicates or external oracle. The evaluator reveals a tuple of three historical responses *only after* selecting an unseen geometry. Paired initial ID sets are frozen per seed. Output reports only campaign aggregates, not coordinates, individual measurements or selected IDs.

## Primary and secondary outcomes

- **Primary:** final simple regret `max(all 600 recorded triplicate means) - max(acquired recorded triplicate means)`, in joules, evaluated by the oracle **after the full campaign**. This is regret against the **best observed noisy triplicate mean in a historical finite pool**, *not* a latent physical optimum or independently measured truth.
- **Secondary:** same regret normalized by range of recorded design mean responses (evaluator-only); fraction of campaigns selecting a design in the source pool's top 10% of noisy observed triplicate means; mean number of acquisitions, mean number of historic physical measurement rows revealed; observed best selected empirical mean. No unmeasured experiment time, monetary cost, energy use, discovery, safety or success probability is imputed.
- Record **paired development seed differences** vs `gp_ard_ei` and `rf_ucb`, without statistical significance claims, independent p-values or post-hoc evidence of scientific superiority.
- Explicitly record all errors and failures; selection from already-observed geometry or exposure of unseen labels is a hard test failure. Raw repeated outcomes **must never be included in committed JSON**.

## What would count as a negative result?

BHS's inherited kernel-portfolio EI fails to match strong GP-ARD or RF on the measured finite pool, is fragile to replicate variation, or incurs much higher compute cost (the latter is **not quantified in this first experiment**). Negative results will be published with equal prominence. If BHS is numerically competitive, it remains *development only*, limited to this historical pool and fixed comparison.

## Scientific limitations and next independent gate

This is a **retrospective replay**: all physically measured results already exist in a public dataset, and source-label availability defines the pool. It is not an actual adaptive physical laboratory trial. Every design has three historical repeats, but they may share batch, printer, material, process or operator effects. The GP noise input estimates variability **within three observations**, not laboratory-calibrated uncertainty. The source labels previously affected v10 diagnostic decisions, so no confirmation on this source is untouched. The model portfolio is statistical, not a causal/mechanistic hypothesis discrimination method.

The true decisive next study requires source-authorized *new physically controlled experiments*, documented instruments/batches, independent evaluation population, calibrated decision risk, matched physical budgets and preregistered acceptance criteria. Until then, hard restrictions remain:
`development_only=true`,
`scored_validation_allowed=false`,
`independent_holdout_used=false`,
`physical_validation_by_bhs=false`,
`causal_identification=false`,
`claim_of_superiority=false`,
`real_savings_measured=false`.

**Execution gate:** `python -m scripts.bhs_replicate_pool_v11` prints the protocol only. `--execute` retrieves the pinned public source and conducts development replay; output is aggregate-only.
