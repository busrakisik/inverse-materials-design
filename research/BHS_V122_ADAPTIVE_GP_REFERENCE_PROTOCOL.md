# BHS v12.2 — Fixed-budget adaptive GP reference: source-independent contracts

**Prepared 7 November 2026. Status: proposed comparator implementation and synthetic software verification only. This document contains no historical or prospective physical outcome scores.**

## Research decision

V11 did not establish superiority for the inherited BHS kernel-portfolio selector against optimized GP–ARD and RF references. The first source-pinned V12 replay failed its original V11 RF parity gate; the failure and exact first-run evidence are retained separately. Subsequent investigation confirmed that changing the presentation order of otherwise identical completed responses can change tree-ensemble acquisition trajectories. V12.1 introduced a stable representation of the *same acquired evidence*. It did not establish time-order invariance of partial observations or repair the first V12 experiment.

The next methodological gap is a matched comparator that makes **individual new-versus-repeat measurement decisions**, not only bundled triplicate purchases. This implementation supplies two transparent *development references* rather than claiming that either reproduces a published optimized sequential design algorithm.

## Fixed action space and budget

- Starting state: six seed-selected geometries, with three actual observations each. All other outcomes hidden. The six initial choices use the existing `initial_geometry_ids` procedure without alteration.
- One action reveals precisely one physical-response value at a previously uncompleted geometry; no geometry may exceed three recorded observations.
- Total response budget: **48** per campaign, including **18** initial responses. The sequential selector receives only known four-dimensional candidate descriptors and a map of already revealed response values.
- Protected seeds **10000–10099** are forbidden. The original development seeds `7, 13, 23, 31, 43` have already been explored, so they cannot produce independent confirmation.
- At most three incompletely measured geometries may be open simultaneously. The comparator additionally reserves enough unspent responses to finish every open geometry; this creates a different completion constraint from the original evidence gate. Both references use the same reservation rule. It prevents a policy from ending with incomplete designs but does **not** isolate the causal contribution of adaptive repetition.

## Noise-aware surrogate

The GP is trained on **one average per acquired geometry**, including partially observed geometries. A pooled within-geometry noise estimate uses only observed replicates:

\[
\widehat{\tau}^{2}=\frac{\sum_{i:\,n_i\geq 2}\sum_{j=1}^{n_i}(y_{ij}-\bar y_i)^2}{\sum_i(n_i-1)}.
\]

The measurement-noise estimate is standardized by the observed group-mean scale and clipped to `[0.001, 1.0]` in standardized variance units. GP training alpha for a measured design is `noise_variance / n_i`; a design with one response receives three times the alpha of a fully observed design under the same pooled variance. The kernel is a four-dimensional Matérn-5/2 GP with a fitted constant amplitude and ARD lengthscales. Its optimizer, bounds, zero restarts and random state are fixed in source. This is a **homoskedastic pooled-noise plug-in**, not a heteroscedastic GP, an external noise calibration or a verified physical uncertainty estimate. Re-fitting hyperparameters after every measurement is part of the method.

## Frozen one-step acquisition scores

Let `j` be an eligible candidate geometry with `n_j` observed responses, latent GP mean `mu_j`, latent predictive variance `v_j`, and estimated individual-response noise variance `tau2`. All candidate descriptors are publicly known; no unseen outcomes enter any score.

**Reference A — GP pooled-noise IVR** (`gp_pooled_noise_ivr`):

\[
S_{\mathrm{IVR}}(j)=\frac{1}{3-n_j}\cdot\frac{\sum_{x\in\mathcal X}\operatorname{Cov}(f(x),f(j))^2}{v_j+\tau^2}.
\]

The variance-reduction numerator/denominator is the Gaussian conditional one-step posterior integrated variance reduction over the fixed candidate pool for the *currently fitted* surrogate. Dividing by remaining responses-to-completion is an explicit heuristic; it is **not** a guaranteed optimal cost model. IVR targets global predictive accuracy and therefore cannot be assumed optimal for identifying the best design.

**Reference B — GP pooled-noise EI** (`gp_pooled_noise_ei`):

\[
S_{\mathrm{EI}}(j)=\frac{\operatorname{EI}_{\mathrm{latent}}(j)}{3-n_j}\cdot\frac{v_j}{v_j+\tau^2}.
\]

The EI incumbent is the highest **completed** acquired triplicate mean in standardized response units, with fixed exploration offset `0.01`. The variance factor discounts a potentially noisy single new measurement. It is a heuristic, **not** an exact noisy expected improvement, knowledge gradient or demonstrated expected value of an experiment.

Action ties resolve to the lowest canonical geometry ID. No unobserved measurement or source-optimum data are permitted in the acquisition function. A real source evaluator would remain separate and would enforce the observation ledger; it is not implemented or called by this source-independent module.

## Mandatory checks before historical testing

1. Compare all scores and expected one-step variance-reduction identities on manufactured numerical examples.
2. Verify exact same next action when the *same* revealed observation multiset is represented in different input orders, and for both references and multiple development seeds.
3. Verify **one response per action**, only the next ordinal, no completed geometry reacquired, at most three incomplete designs and exactly 48 total observations with no uncompleted endpoints in synthetic complete-budget runs.
4. Show that no protected seeds, extra labels, invalid/nonfinite input or inconsistent step counts are accepted.
5. Keep the original V12 and V12.1 tests passing in pinned numerical CI.
6. Ensure CI never loads the historical source or produces physical-performance scores.

Only after these checks should any **separately approved, precommitted** retrospective development protocol compare V12.0 evidence gate, bundled GP, and both adaptive GP references under the same acquired-response budget. That protocol must freeze multiple within-geometry order permutations, matched candidate pools, source hash, sensitivity summaries, and completed-design decision loss *before* revealing results. Additional use of an already inspected historical archive remains development, not independent validation. Prospective physical data with authentic time/batch provenance and domain-expert oversight are required for a generalizable claim.

## Prior art and distinctions

- Binois, Huang, Gramacy and Ludkovski, *Replication or Exploration? Sequential Design for Stochastic Simulation Experiments*, **Technometrics** 61(1), 7–23 (2019), DOI: 10.1080/00401706.2018.1469433. This paper develops lookahead replication/exploration design; the present implementation is intentionally simpler and must not be advertised as its reproduction.
- Binois and Gramacy, *hetGP: Heteroskedastic Gaussian Process Modeling and Sequential Design in R*, **Journal of Statistical Software** 98(13) (2021), DOI: 10.18637/jss.v098.i13. Unlike hetGP, this reference uses an estimated shared noise variance rather than a learned input-dependent noise field.

## Evidence restrictions

`development_only=true`  
`scored_validation_allowed=false`  
`independent_holdout_used=false`  
`physical_validation_by_bhs=false`  
`causal_identification=false`  
`calibrated_uncertainty_proven=false`  
`claim_of_superiority=false`  
`real_savings_measured=false`  
`reserved_nist_seeds_used=false`

No changed V11 negative results, no revised V12 first-run evidence, no release, no default-branch merge, no history rewrite and no automatic laboratory recommendations.
