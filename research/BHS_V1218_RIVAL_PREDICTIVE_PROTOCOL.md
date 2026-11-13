# BHS V12.18 — Frozen rival predictive-structure prototype protocol

**13 November 2026. Frozen before implementing or running V12.18 tests. No published measured response may be loaded, trained on, rescored or selected during this stage.**

## Research purpose

Build an **operational two-model Bayesian evidence and experimental-design component**, without misrepresenting rival *predictive functional forms* as independently established physical deformation mechanisms or complete BHS. This is a necessary executable stepping stone, not publication-ready performance or a causal conclusion.

Scientific external context: Gongora et al., *Science Advances* **6** (2020), eaaz1708, DOI `10.1126/sciadv.aaz1708`, original preprinted crossed-barrel design `(n, theta, r, t)` and subsequent experimentally measured compressive toughness `U` in joules. The paper states design parameters are used to generate printable geometry before weighing and measuring components; force–displacement curves are collected separately. The old V11 dataset exposed to BHS contains four public design coordinates and historical toughness replicates; independently matched curve-level failure-mode outcomes are NOT verified within the old V11 evaluation. Do not invent such records. Existing author data and physical processing noise are not controlled by this code.

The original V11 equal-budget statistical portfolio lost to GP–ARD EI and RF–UCB on five retrospective **development** seeds: means `7.363 J GP`, `8.983 J RF`, `9.368 J old BHS kernel portfolio`, `15.951 J random`. V11 did NOT evaluate the complete BHS model. All old negative results are immutable.

## Two competing quantitative *predictive* hypotheses, not physical mechanisms

- `H_ADD`: measured scalar toughness is approximately an **additive linear function** of four dimensionless and fixed premeasurement geometric design variables. Features `[1, u_n, u_theta, u_r, u_t]`.
- `H_TWIST_THICKNESS`: the same additive relationship plus **an interaction** between twist angle and wall thickness. Features `[1, u_n, u_theta, u_r, u_t, u_theta * u_t]`.

Both are falsifiable predictive structural families through their distinct heldout predictions, but they are NESTED models (H_ADD is the zero-interaction special case), not mutually exclusive physical failure mechanisms. Observation of better interaction-model predictive evidence does NOT prove buckling, ductility, material phase or causal deformation. The chosen interaction is an explicitly **provisional model-development choice**, not an effect certified by the original paper. It must not be presented as a post-hoc discovery.

Predeclared dimensionless transformations, computed only from the **public design recipe**, without fitting a scaler to hidden outcomes:

`u_n = n/12 - 1`; `u_theta = theta_deg/90 - 1`; `u_r = r_mm/2.5 - 1`; `u_t = t_mm/1 - 1`.

These normalization constants are fixed engineering references, **not fitted physical hyperparameters**. Source variables: `n` positive integer number of columns; `theta_deg` finite in 0..180; `r_mm > 0`; `0 < t_mm <= r_mm`. Complete candidate descriptors may be known **before** the specific compression measurement; actual historical timestamp lineage, precise manufacturing cost and independent prospective testing are not established by this software exercise. Measured toughness is never a public feature.

## Fixed Bayesian numerical contract

Equal initial competing model priors 0.5/0.5. Each model assumes a conjugate Gaussian linear coefficient prior `beta ~ N(0, 10^2 I)` with **fixed assumed** i.i.d. observation variance `5^2 joule^2`. The `5 J` figure is a deliberately transparent, uncalibrated engineering-development placeholder (the original paper initialized GP observational noise at 5 J), not certified experimental measurement noise or an available prospective tuning parameter. The Gaussian likelihood can assign mass to impossible negative toughness, another **known model misspecification**. Its consequences must be audited before real scoring.

Conditional regression posterior under each model uses ONLY previously observed selected design–measurement pairs; posterior model odds update by the exact sequential marginal predictive density of the **newly revealed** outcome. No unrevealed candidate labels, optimum, external source oracle or retrospective outcome-derived features are allowed inside the model. Preserve exact normalization and finite numerical invariants, reject duplicate/unknown observed IDs, malformed nonphysical design descriptors and nonfinite outcomes.

**Selection objective** is explicitly defined as one-step expected information gain (EIG) about the two competing predictive model identities, calculated from the **current** model-mixture posterior predictive distribution by frozen **16-point Gauss–Hermite quadrature**. This is not expected-improvement optimization of toughness, compute scheduling, multi-fidelity optimization, or MCTS. Select highest EIG among unobserved candidate designs; break exact ties by lexicographic ID. The model cannot use measured outcomes of not-yet-selected designs. Candidate computational scores may be inspected only under synthetic fixtures for test and debugging; no published real response scores in V12.18.

Distinguish the **two different resource notions**: each real observation costs one notional response in the toy contract, but no verified laboratory minutes, printer hours, GPU-hours or financial savings. EIG is a statistical information objective about predictive models, not proof of physical mechanism identifiability.

## Frozen synthetic-only contracts

- Prior model weights `(0.5,0.5)`; unobserved label values must not change initial choice.
- Analytically check 1D and mixed linear conjugate posterior against independent closed-form values; mathematical evidence updates from **previously supplied synthetic responses** only.
- Invariance to unused candidate-ID ordering and unobserved labels; exact same visible history produces same choice.
- Hypothesis identity matters: predictions for at least one design with nonzero `u_theta * u_t` have distinct uncertainty under H_ADD versus H_TWIST_THICKNESS, and model posterior changes on a synthetic response.
- Identical candidate metadata and prior observations form the entire decision API; unknown, duplicate or unearned data rejected.
- Source-code checks prove **no external measurements or source downloads** occur in test/implementation imports.
- Compute EIG finite and nonnegative up to a stated quadrature numerical tolerance; reject nonfinite posterior or pathological numeric inputs rather than fabricating certainty.
- Flags remain **`development_only=true`, `synthetic_protocol_only=true`, `scored_validation_allowed=false`, `physical_mechanisms_identified=false`, `scientific_likelihood_calibrated=false`, `full_bhs_fair_comparison_ready=false`, `independent_holdout_used=false`, `claim_of_superiority=false`, `real_savings_measured=false`, `laboratory_action_allowed=false`**.

## What remains before authentic full-BHS evaluation

Independent physical interpretation of rival mechanisms, relevant curve-level failure-mode observations, realistic likelihood and noise validation, a real acquisition plan at matched cost, observation-contingent MCTS if a nonmyopic claim is intended, training-only hyperparameters, a heldout/prospective source not previously inspected, authentic candidate decision chronology and strong GP/RF/expert baselines. Do not use original V11 development seeds as independent future evaluation. No existing draft PR/release/default branch, old negative study, or protected NIST seeds `10000..10099` may be edited.

**Expected stage verdict:** functioning mathematical hypothesis-discrimination component may be established by **synthetic** tests, but **NO GO for empirical performance claims** until all scientific and data-origin criteria pass.
